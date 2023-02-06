/* begin: blocks/test/test.view.js */
(function () {
    var views = home.desktopViews['test'].ru;
(function(views) {
    'use strict';

    //INCLUDE("blocks/test/test2.js");

    views('test_0', function test_0 () {
        var key = '1';
        return this.l10n('smth.subkey_' + key);
    });

}(views));
})();
/* end: blocks/test/test.view.js */
