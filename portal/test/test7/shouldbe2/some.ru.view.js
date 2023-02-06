(function () {
    var views = home.desktopViews.ru;
/* begin: blocks/test2.view.js */
(function(views) {
    'use strict';

    views('test_1', 'text');

}(views));
/* end: blocks/test2.view.js */
/* begin: blocks/test.view.js */
(function(views) {
    'use strict';

    views('test_0', function test_0 () {
        return ["a","b","c"][1];
    });

}(views));
/* end: blocks/test.view.js */
})();
