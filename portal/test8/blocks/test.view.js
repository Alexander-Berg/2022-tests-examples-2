(function(views) {
    'use strict';

    views('test_0', function() {
        return this.l10n(
            'array_smth.' + this.property
        )[1];
    });

}(views));
