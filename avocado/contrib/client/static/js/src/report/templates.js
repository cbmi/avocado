require.def('report/templates', ['lib/jquery.jqote2'], function() {
    return {
        header: $.jqotec('<th class="header <%= this.direction %>"><span><%= this.name %></th>'),
        row: $.jqotec([
            '<tr>',
                '<td><input type="checkbox">',
                '<% for(var i=0;i<this.length;i++){ %><td>this[i]</td><% } %>',
            '</tr>'
        ].join(''))
    };
}); 