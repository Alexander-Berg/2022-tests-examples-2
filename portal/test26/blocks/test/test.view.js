(function(views) {
    'use strict';

    views('test_0', function() {
        var key = '1';
        return this.l10n('smth.subkey_' + key);
    });

}(views));
