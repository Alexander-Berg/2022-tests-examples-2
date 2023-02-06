(function () {
    var views = home.desktopViews.uk;
/* begin: blocks/test.view.js */
(function(views) {
    'use strict';

    views('test_0', function test_0 () {
        var obj = {"val0":"ukabc","val1":"ukdef","val3":"ukght","array":["uka","ukb","ukc"]};
        return obj.val1 + ';' + obj.array.join() + ';' + JSON.stringify(obj);
    });

}(views));
/* end: blocks/test.view.js */
})();
