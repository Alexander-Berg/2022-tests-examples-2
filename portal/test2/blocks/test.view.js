(function(views) {
    'use strict';

    views('test_0', function() {
        return this.l10n('level0.level1.' + this.id);
    });

}(views));
