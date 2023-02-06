(function () {
    var views = home.desktopViews.ru;
/* begin: transforms-promise/blocks/test.view.js */
// wait: done
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
/* end: transforms-promise/blocks/test.view.js */
})();
