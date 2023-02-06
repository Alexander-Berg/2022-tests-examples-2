/* begin: blocks/test/test.view.js */
(function () {
    var views = home.desktopViews['test'];
(function(views) {
    'use strict';

    var data = RAWINC("blocks/test/test2.js");

    views('test_0', function() {
        var key = '1';
        return data + this.l10n('smth.subkey_' + key);
    });

}(views));
})();
/* end: blocks/test/test.view.js */
