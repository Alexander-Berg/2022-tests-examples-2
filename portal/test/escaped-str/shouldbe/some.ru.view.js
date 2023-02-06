(function () {
    var views = home.desktopViews.ru;
/* begin: blocks/test.view.js */
(function(views) {
    'use strict';

    views('test2_0', function test2_0 () {
        //noinspection JSUnusedLocalSymbols
        var local = this;
        return 'another " quot\\s' + 'abc';
    });

}(views));
/* end: blocks/test.view.js */
})();
