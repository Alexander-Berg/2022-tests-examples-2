(function () {
    var views = home.desktopViews.ru;
/* begin: blocks/test.view.js */
(function(views) {
    'use strict';

    var abc = "(function(views) {\n    'use strict';\n\n    views('test2_0', function test2_0 () {\n        //noinspection JSUnusedLocalSymbols\n        var local = this;\n        return local.l10n('title') + local.l10n(\"title\");\n    });\n\n    views('test2_1', function test2_1 () {\n        var local = this,\n            id = 'inner';\n        return local.l10n('sub.' + (id.substr(0, 2)) + '.tratata');\n    });\n\n    views('test2_2', function test2_2 () {\n        return views('test2_0', {});\n    });\n\n}(views));\n";

    views('test_0',
        'abc'
    );

}(views));
/* end: blocks/test.view.js */
})();
