(function () {
    var views = home.desktopViews;
/* begin: blocks/test.view.js */
(function(views) {
    'use strict';

    views('test_0', function() {
        var obj = this.l10n('obj');
        return obj.val1 + ';' + obj.array.join() + ';' + JSON.stringify(obj);
    });

}(views));
/* end: blocks/test.view.js */
})();
