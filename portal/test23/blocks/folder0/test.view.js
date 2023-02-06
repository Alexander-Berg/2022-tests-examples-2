(function(views) {
    'use strict';

    views('test_0', function() {
        var title = 'title';
        return this.l10n('page.' + title);
    });

}(views));
