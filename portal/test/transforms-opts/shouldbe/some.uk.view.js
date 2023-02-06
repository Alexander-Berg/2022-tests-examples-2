(function () {
    var views = home.desktopViews.uk;
/* begin: transforms-opts/blocks/test.view.js */
// Generated at Tue Feb 16 2016 19:27:17 GMT+0300 (MSK), file: (transforms-opts/blocks/test.view.js)
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
/* end: transforms-opts/blocks/test.view.js */
})();
