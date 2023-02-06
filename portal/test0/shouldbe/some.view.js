(function () {
    var views = home.desktopViews;
/* begin: blocks/test.view.js */
(function(views) {
    'use strict';

    var sample;

    views('test_0',
        '[% l10n:title %]'
    );

    views('test_1',
        "[% l10n:title %]"
    );

    views('test_2',
        '[% l10n:quot0 %]'
    );

    views('test_3',
        "[% l10n:quot0 %]"
    );

    views('test_4',
        '[% l10n:quot1 %]'
    );

    views('test_5',
        "[% l10n:quot1 %]"
    );

    views('test_6',
        'a[% l10n:sub.in %]b'
    );

    views('test_7',
        'a[% l10n:sub.in %]b[% l10n:title %]c'
    );

    sample = 'abc';

    home.alert(sample);

}(views));
/* end: blocks/test.view.js */
/* begin: blocks/test2.view.js */
(function(views) {
    'use strict';

    views('test2_0', function() {
        //noinspection JSUnusedLocalSymbols
        var local = this;
        return local.l10n('title') + local.l10n("title");
    });

    views('test2_1', function() {
        var local = this,
            id = 'inner';
        return local.l10n('sub.' + (id.substr(0, 2)) + '.tratata');
    });

    views('test2_2', function() {
        return views('test2_0', {});
    });

}(views));
/* end: blocks/test2.view.js */
/* begin: blocks/test3.view.js */
(function(views) {
    'use strict';

    views('test3_0',
        '[% l10n:level0.level1.level2.key %]'
    );

    views('test3_1', function() {
        var local = this,
            id = 'inner';
        return local.l10n('level0.level1.' + (id.substr(0, 2)) + '.tratata');
    });

}(views));
/* end: blocks/test3.view.js */
})();
