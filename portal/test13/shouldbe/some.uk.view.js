/* begin: blocks/test/test.view.js */
(function () {
    var views = home.desktopViews['test'].uk;
(function(views) {
    'use strict';

    function abc () {
    return 'common value_uk';
}

var bcd = "asd\"" + '" + 123';
;

    var test2 = "function abc () {\n    return 'common value_uk';\n}\n\nvar bcd = \"asd\\\"\" + '\" + 123';\n";

    views('test_0', function test_0 () {
        var key = '1';
        return this.l10n('smth.subkey_' + key);
    });

}(views));
})();
/* end: blocks/test/test.view.js */
