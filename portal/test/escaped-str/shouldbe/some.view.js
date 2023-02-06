(function () {
    var views = home.desktopViews;
/* begin: blocks/test.view.js */
(function(views) {
    'use strict';

    views('test2_0', function() {
        //noinspection JSUnusedLocalSymbols
        var local = this;
        return local.l10n('quot1') + local.l10n("title");
    });

}(views));
/* end: blocks/test.view.js */
})();
