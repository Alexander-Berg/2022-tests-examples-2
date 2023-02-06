(function () {
    var views = home.desktopViews.ru;
/* begin: api-run/blocks/test.view.js */
(function(views) {
    'use strict';

    var sample;

    views('test_0',
        'abc'
    );

    views('test_1',
        "abc"
    );

    views('test_2',
        'д\'артаньян'
    );

    views('test_3',
        "д'артаньян"
    );

    views('test_4',
        'another " quot'
    );

    views('test_5',
        "another \" quot"
    );

    views('test_6',
        'a123b'
    );

    views('test_7',
        'a123babcc'
    );

    sample = 'abc';

    home.alert(sample);

}(views));
/* end: api-run/blocks/test.view.js */
/* begin: api-run/blocks/test2.view.js */
(function(views) {
    'use strict';

    views('test2_0', function test2_0 () {
        //noinspection JSUnusedLocalSymbols
        var local = this;
        return 'abc' + 'abc';
    });

    views('test2_1', function test2_1 () {
        var local = this,
            id = 'inner';
        return local.l10n('sub.' + (id.substr(0, 2)) + '.tratata');
    });

    views('test2_2', function test2_2 () {
        return views('test2_0', {});
    });

}(views));
/* end: api-run/blocks/test2.view.js */
/* begin: api-run/blocks/test3.view.js */
(function(views) {
    'use strict';

    views('test3_0',
        'value'
    );

    views('test3_1', function test3_1 () {
        var local = this,
            id = 'inner';
        return local.l10n('level0.level1.' + (id.substr(0, 2)) + '.tratata');
    });

}(views));
/* end: api-run/blocks/test3.view.js */
})();
