(function () {
    var views = home.desktopViews.ru;
/* begin: blocks/test.view.js */
(function(views) {
    'use strict';

    views('test_0', function test_0 () {
        return this.l10n(
            'array_smth.' + this.property
        )[1];
    });

}(views));
/* end: blocks/test.view.js */
})();
