(function(views) {
    'use strict';

    views('test3_0',
        '[% l10n:level0.level1.level2.key %]'
    );

    views('test3_1', function() {
        var local = this,
            id = 'inner';
        return local.l10n('level0.level1.' + (id.substr(0, 2)) + '.tratata');
    });

}(views));
