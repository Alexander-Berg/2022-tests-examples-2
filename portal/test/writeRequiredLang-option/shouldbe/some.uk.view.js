(function () {
    var views = home.desktopViews.uk;
/* begin: blocks/test.view.js */
(function(views) {
    'use strict';

    var sample;

    views('test_0',
        'uk_abc'
    );

    views('test_1',
        "uk_abc"
    );

    views('test_2',
        'uk_д\'артаньян'
    );

    views('test_3',
        "uk_д'артаньян"
    );

    views('test_4',
        'uk_another " quot'
    );

    views('test_5',
        "uk_another \" quot"
    );

    views('test_6',
        'auk_123b'
    );

    views('test_7',
        'auk_123buk_abcc'
    );

    sample = 'abc';

    home.alert(sample);

}(views));
/* end: blocks/test.view.js */
/* begin: blocks/test2.view.js */
(function(views) {
    'use strict';

    views('test2_0', function test2_0 () {
        //noinspection JSUnusedLocalSymbols
        var local = this;
        return 'uk_abc' + 'uk_abc';
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
/* end: blocks/test2.view.js */
/* begin: blocks/test3.view.js */
(function(views) {
    'use strict';

    views('test3_0',
        'uk_value'
    );

    views('test3_1', function test3_1 () {
        var local = this,
            id = 'inner';
        return local.l10n('level0.level1.' + (id.substr(0, 2)) + '.tratata');
    });

}(views));
/* end: blocks/test3.view.js */
})();
