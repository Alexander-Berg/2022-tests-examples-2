(function () {
    var views = home.desktopViews.ru;
/* begin: blocks/test.view.js */
(function(views) {
    'use strict';

    views('test_0', function test_0 () {
        var obj = {"val0":"abc","val1":"def","val3":"ght","array":["a","b","c"]};
        return obj.val1 + ';' + obj.array.join() + ';' + JSON.stringify(obj);
    });

}(views));
/* end: blocks/test.view.js */
})();
