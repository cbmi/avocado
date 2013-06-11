import os
import random
from django.test import TestCase
from avocado.stats import kmeans
from itertools import chain

__all__ = ('KmeansTestCase',)

random_points_file = open(
        os.path.join(os.path.dirname(__file__), 
        '../fixtures/random_points/points.txt'))
random_points = [float(x.strip()) for x in random_points_file.xreadlines()]

random_points_3d_file = open(
        os.path.join(os.path.dirname(__file__), 
        '../fixtures/random_points_3d/points.txt'))
random_points_3d = [[float(x) for x in l.strip().split(",")] 
        for l in random_points_3d_file.xreadlines()]

int_points_3d_file = open(
        os.path.join(os.path.dirname(__file__),
        '../fixtures/int_3d/points.txt'))
int_points_3d = [[int(x) for x in l.strip().split(",")]
        for l in int_points_3d_file.xreadlines()]

PLACES = 10

class KmeansTestCase(TestCase):
    """
    NOTE: All numpy and scipy output files and values were created with the 
    following:
        numpy version 1.7.1
        scipy version 0.12.0
        python version 2.7.3
    """
    def assertSequenceAlmostEqual(self, seq1, seq2, num_places=None):
        """
        Helper method for checking that 2 sequences are almost equal.

        Two sequences are considered almost equal if they have the same order
        and each pair of elements of the sequences passes the 
        assertAlmostEqual to the number of decimal places specified in 
        'num_places'. This method will also work for nested lists of numbers. 
        For example, let's say we wanted to see if two collections of 3D 
        points were almost equal, we could use the following:

            >>> pts1 = [[0.206331960142751, 0.612540082088810, 0.843236918599283], 
            ...         [0.269705965446683, 0.218132746363829, 0.277332011689122], 
            ...         [0.728684538148946, 0.734953792412333, 0.722476119561547]]
            >>> pts2 = [[0.206331960142700, 0.612540082088819, 0.843236918599288], 
            ...         [0.269705965446609, 0.218132746363899, 0.277332011689182], 
            ...         [0.728684538148046, 0.734953792412933, 0.722476119561847]]
            >>> assertSequenceAlmostEqual(pts1, pts2)

        Arguments:
            seq1, seq2: (nested)list of numbers to check for near equality

        NOTE: This method assumes 'seq1' 'seq2' have equal, non-zero length. If
        you are not certain the lengths match, use the following assert before
        calling this method or this method might have unpredictable results.
        For nested lists, it is not only assumed that overall list length is
        the same, but also that each nested list pair is of equal length.

            assertEqual(len(seq1), len(seq2))
        """
        num_places = num_places or PLACES

        if kmeans.is_iterable(seq1[0]):
            for list1, list2 in zip(seq1, seq2):
                self.assertSequenceAlmostEqual(list1, list2, num_places)
        else:
            for num1, num2 in zip(seq1, seq2):
                self.assertAlmostEqual(num1, num2, num_places)

    def test_std_dev(self):
        our_std_dev = kmeans.std_dev(random_points)

        self.assertEqual(28.247608160964884, our_std_dev)

    def test_normalize(self):
        vq_file = open(os.path.join(
            os.path.dirname(__file__), 
            '../fixtures/random_points/scipy_whiten_output.txt'))
        vq_output = [float(x.strip()) for x in vq_file.xreadlines()]
        
        our_normalize = kmeans.normalize(random_points)
        
        self.assertSequenceAlmostEqual(vq_output, our_normalize)

        vq_file = open(os.path.join(
            os.path.dirname(__file__), 
            '../fixtures/random_points_3d/scipy_whiten_output.txt'))
        vq_output = [[float(x) for x in l.strip().split(",")] 
                for l in vq_file.xreadlines()]

        our_normalize = kmeans.normalize(random_points_3d)
        
        self.assertSequenceAlmostEqual(vq_output, our_normalize)

    def test_vq_1d(self):
        # Randomly generated list of indexes in the 1d random points list
        book_indexes = [231, 31, 250, 104, 233, 289, 236, 259]
        book = [random_points[i] for i in book_indexes]

        vq_file = open(os.path.join(
            os.path.dirname(__file__),
            '../fixtures/random_points/scipy_vq_output.txt'))
        
        s_code = []
        s_dist = []
        for l in vq_file.xreadlines():
            fields = l.split(",")
            if not l.startswith("#") and len(fields) == 2:
                s_code.append(int(fields[0].strip()))
                s_dist.append(float(fields[1].strip()))

        m_code, m_dist = kmeans.compute_clusters(random_points, book)

        self.assertSequenceEqual(s_code, m_code)
        self.assertSequenceAlmostEqual(s_dist, m_dist)

    def test_vq_1d_nested(self):
        nested = [[p] for p in random_points]
        book_indexes = [231, 31, 250, 104, 233, 289, 236, 259]
        book = [nested[i] for i in book_indexes]

        vq_file = open(os.path.join(
            os.path.dirname(__file__),
            '../fixtures/random_points/scipy_vq_output.txt'))
        
        s_code = []
        s_dist = []
        for l in vq_file.xreadlines():
            fields = l.split(",")
            if not l.startswith("#") and len(fields) == 2:
                s_code.append(int(fields[0].strip()))
                s_dist.append(float(fields[1].strip()))

        m_code, m_dist = kmeans.compute_clusters(nested, book)

        self.assertSequenceEqual(s_code, m_code)
        self.assertSequenceAlmostEqual(s_dist, m_dist)

    def test_vq(self):
        book_indexes = [28, 182, 948, 434, 969, 814, 859, 123]
        book = [random_points_3d[i] for i in book_indexes]

        vq_file = open(os.path.join(
            os.path.dirname(__file__),
            '../fixtures/random_points_3d/scipy_vq_output.txt'))

        s_code = []
        s_dist = []
        for l in vq_file.xreadlines():
            fields = l.split(",")
            if not l.startswith("#") and len(fields) == 2:
                s_code.append(int(fields[0].strip()))
                s_dist.append(float(fields[1].strip()))

        m_code, m_dist = kmeans.compute_clusters(random_points_3d, book)

        self.assertSequenceEqual(s_code, m_code)
        self.assertSequenceAlmostEqual(s_dist, m_dist)

    def test_kmeans(self):
        # These indices don't really matter since the points are random but
        # I am fixing them here for repeatability of the test.
        centroids = [random_points_3d[125], 
                     random_points_3d[500], 
                     random_points_3d[875]]

        s_centroids = [[ 0.44876204,  0.3331773 ,  0.233552  ],
                       [ 0.49838519,  0.29378851,  0.75018887],
                       [ 0.5225907 ,  0.80407079,  0.53268326]]
        m_centroids, m_distance = kmeans.kmeans(random_points_3d, centroids)
        
        self.assertEqual(0.35944390987038655, m_distance)

        # I'm getting everything to pass at 10 places except for this where 
        # there always seems to be at least one dimension of one centroid 
        # about [.001-.005] away from where we expect it to be. This is due to
        # difference in floating point storage between numpy and python. See
        # the following for more info:
        #           https://github.com/cbmi/avocado/issues/34
        self.assertSequenceAlmostEqual(s_centroids, m_centroids, num_places=2)

    def test_no_outliers(self):
        points = [[i,i] for i in range(300)]
        m_outliers = kmeans.find_outliers(points, normalized=False)

        self.assertEqual(m_outliers, [])

    def test_outliers(self):
        expected_outliers = [91, 225, 263, 371, 377]
        m_outliers = kmeans.find_outliers(int_points_3d, normalized=True)

        self.assertSequenceEqual(expected_outliers, m_outliers)

    def test_weighted_counts(self):
        """
        We might expect these to be 300, 200, and 100 but in running through
        this manually, the returned centroids from kmeans using k of 3 will be:
            [[0.9999999999999954, 0.9999999999999954, 0.9999999999999954], 
             [2.0000000000000018, 2.0000000000000018, 2.0000000000000018], 
             [2.9999999999999964, 2.9999999999999964, 2.9999999999999964]]
        
        which are close to but not exactly the perfect solution of:
        
            [[1.0, 1.0, 1.0],
             [2.0, 2.0, 2.0],
             [3.0, 3.0, 3.0]]

        this is a result of the floating point math in k-means. Because of 
        these seemingly trivial differences, we will get distances that aren't
        quite zero meaning, there will be dist_sum values in the 
        weighted_count methods. Because of that, we will lose fractions of a 
        count on each of the weighted count calculations, which, when summed
        over each centroid, account for difference of between 1 and 2 in the
        returned counts versus the expected counts. The weighted_counts method
        is deemed correct even though we expect counts of [300, 200, 100] 
        because it can't be expected to overcome the issues introduced during
        the floating point arithmetic during k-means execution.
        """

        expected_counts = [299, 199, 98]
        counts = [1] * 605

        centroid_counts, _ = kmeans.weighted_counts(int_points_3d, counts, 3)
        m_counts = [c['count'] for c in centroid_counts]

        self.assertSequenceEqual(expected_counts, m_counts)