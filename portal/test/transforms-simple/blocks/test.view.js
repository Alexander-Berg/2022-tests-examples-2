(function(views) {
    'use strict';

    var sample;

    views('test_0',
        '[% l10n:title %]'
    );

    views('test_1',
        "[% l10n:title %]"
    );

    views('test_2',
        '[% l10n:quot0 %]'
    );

    views('test_3',
        "[% l10n:quot0 %]"
    );

    views('test_4',
        '[% l10n:quot1 %]'
    );

    views('test_5',
        "[% l10n:quot1 %]"
    );

    views('test_6',
        'a[% l10n:sub.in %]b'
    );

    views('test_7',
        'a[% l10n:sub.in %]b[% l10n:title %]c'
    );

    sample = 'abc';

    home.alert(sample);

}(views));
