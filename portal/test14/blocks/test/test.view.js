(function(views) {
    'use strict';

    INCLUDE("blocks/test/test2.js");

    var test2 = RAWINC("blocks/test/test2.js");

    views('test_0', '[% l10n:test %]');

}(views));
