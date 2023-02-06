(function(views) {
    'use strict';

    views('test2_0', function() {
        //noinspection JSUnusedLocalSymbols
        var local = this;
        return local.l10n('title') + local.l10n("title");
    });

    views('test2_1', function() {
        var local = this,
            id = 'inner';
        return local.l10n('sub.' + (id.substr(0, 2)) + '.tratata');
    });

    views('test2_2', function() {
        return views('test2_0', {});
    });

}(views));
