(function () {
    var views = home.desktopViews.uk;
/* begin: transforms-promise/blocks/test.view.js */
// wait: done
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
/* end: transforms-promise/blocks/test.view.js */
})();
