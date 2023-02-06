(function(views) {
    'use strict';

    //INCLUDE("blocks/test/test2.js");

    views('test_0', function() {
        var key = '1';
        return this.l10n('smth.subkey_' + key);
    });

}(views));
