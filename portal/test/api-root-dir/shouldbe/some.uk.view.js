(function () {
    var views = home.desktopViews.uk;
/* begin: blocks/test.view.js */
(function(views) {
    'use strict';

    var sample;

    (function(views) {
    'use strict';

    views('test2_0', function test2_0 () {
        //noinspection JSUnusedLocalSymbols
        var local = this;
        return 'uk_abc' + 'uk_abc';
    });

    views('test2_1', function test2_1 () {
        var local = this,
            id = 'inner';
        return local.l10n('sub.' + (id.substr(0, 2)) + '.tratata');
    });

    views('test2_2', function test2_2 () {
        return views('test2_0', {});
    });

}(views));
;

}(views));
/* end: blocks/test.view.js */
})();
