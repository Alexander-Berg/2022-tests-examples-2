/* begin: blocks/test/test.view.js */
(function () {
    var views = home.desktopViews['test'].ru;
(function(views) {
    'use strict';

    function abc () {
    return 'common value';
}

var bcd = "asd\"" + '" + 123';
;

    views('test_0', function test_0 () {
        var key = '1';
        return this.l10n('smth.subkey_' + key);
    });

}(views));
})();
/* end: blocks/test/test.view.js */
