/* begin: blocks/test/test.view.js */
(function () {
    var views = home.desktopViews['test'].ru;
(function(views) {
    'use strict';

    views('test_0', function test_0 () {
        var key = '1';
        return this.l10n('smth.subkey_' + key);
    });

}(views));
})();
/* end: blocks/test/test.view.js */
/* begin: blocks/test2/test2.view.js */
(function () {
    var views = home.desktopViews['test2'].ru;
(function(views) {
    'use strict';

    views('test_1', 'something');

}(views));
})();
/* end: blocks/test2/test2.view.js */
