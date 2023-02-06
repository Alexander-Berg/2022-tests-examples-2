/* begin: blocks/test/test.view.js */
(function () {
    var views = home.desktopViews['test'].uk;
(function(views) {
    'use strict';

    var data = "function abc () {\n    return 'common value_uk';\n}\n\nvar bcd = \"asd\\\"\" + '\" + 123';\n";

    views('test_0', function test_0 () {
        var key = '1';
        return data + this.l10n('smth.subkey_' + key);
    });

}(views));
})();
/* end: blocks/test/test.view.js */
