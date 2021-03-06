import logging
from django.test import TransactionTestCase
from django.contrib.auth.models import User
from django.contrib.sessions.backends.cache import SessionStore
from django.http import HttpRequest
from avocado.events import usage
from avocado.events.models import Log
from avocado.models import DataField


class MockHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }


# Setup a mock handler
logger = logging.getLogger(usage.__name__)
mock_handler = MockHandler()
logger.addHandler(mock_handler)


class LogTestCase(TransactionTestCase):
    def test_event(self):
        usage.log('test', async=False)
        self.assertEqual(Log.objects.count(), 1)

    def test_instance(self):
        f = DataField(app_name='avocado',
                      model_name='datafield',
                      field_name='name')
        f.save()

        usage.log('test', instance=f, async=False)
        event = Log.objects.all()[0]
        self.assertEqual(event.content_object, f)

    def test_model(self):
        usage.log('test', model=DataField, async=False)
        event = Log.objects.all()[0]
        self.assertEqual(event.content_type.model_class(), DataField)

    def test_data(self):
        usage.log('test', data={'some': 'data'}, async=False)
        event = Log.objects.all()[0]
        self.assertEqual(event.data, {'some': 'data'})

    def test_error(self):
        # Pass non-JSON serializable data
        usage.log('test', data={'some': TransactionTestCase}, async=False)
        self.assertEqual(Log.objects.count(), 0)
        self.assertEqual(len(mock_handler.messages['error']), 1)

    def test_request(self):
        user = User.objects.create_user('root', 'root')
        session = SessionStore()
        session.save()

        request = HttpRequest()
        request.user = user
        request.session = session

        usage.log('test', request=request, async=False)
        event = Log.objects.all()[0]
        self.assertEqual(event.user, user)
        self.assertEqual(event.session_key, request.session.session_key)
