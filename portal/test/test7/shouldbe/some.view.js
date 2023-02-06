(function () {
    var views = home.desktopViews;
/* begin: blocks/test.view.js */
(function(views) {
    'use strict';

    views('test_0', function() {
        return this.l10n('array')[1];
    });

}(views));
/* end: blocks/test.view.js */
/* begin: blocks/test2.view.js */
(function(views) {
    'use strict';

    views('test_1', '[% l10n:title %]');

}(views));
/* end: blocks/test2.view.js */
})();
