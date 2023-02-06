(function () {
    var views = home.desktopViews.ru;
/* begin: blocks/test.view.js */
(function(views) {
    'use strict';

    views('test_0', function test_0 () {
        var key = '1';
        return this.l10n('smth.subkey_' + key);
    });

}(views));
/* end: blocks/test.view.js */
})();
