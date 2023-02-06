/* begin: blocks/test/test.view.js */
(function () {
    var views = home.desktopViews['test'];
(function(views) {
    'use strict';

    INCLUDE("blocks/test/test2.js");

    var test2 = RAWINC("blocks/test/test2.js");

    views('test_0', '[% l10n:test %]');

}(views));
})();
/* end: blocks/test/test.view.js */
