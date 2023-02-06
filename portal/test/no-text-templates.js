const rule = require('../lib/no-text-templates'),
    RuleTester = require('eslint').RuleTester;

const ruleTester = new RuleTester({env: {es6: true}, globals: {views: true}});

ruleTester.run('no-text-templates', rule, {
    valid: [
        {
            code: "views('aba', function () {})"
        },
        {
            code: "views.cached('aba', function () {})"
        },
        {
            code: "views('aba', () => {})"
        },
        {
            code: "views.cached('aba', () => {})"
        }
    ],

    invalid: [
        {
            code: "views('aba', 'qweqwe')",
            errors: [{message: /should be wrapped/}],
            output: "views('aba', function () {\n\treturn 'qweqwe';\n})"
        },
        {
            code: "views('aba', 'qw[% qq %]eqwe')",
            errors: [{message: /should be wrapped/}],
            output: "views('aba', 'qw[% qq %]eqwe')"
        },
        {
            code: "views('aba', 'qwe' + 'qwe')",
            errors: [{message: /should be wrapped/}],
            output: "views('aba', function () {\n\treturn 'qwe' + 'qwe';\n})"
        },
        {
            code: "views('aba', '[% x %]' + 'qwe')",
            errors: [{message: /should be wrapped/}],
            output: "views('aba', '[% x %]' + 'qwe')"
        },
        {
            code: "var t = 'qweqwe';\nviews('aba', t)",
            errors: [{message: /should be wrapped/}]
        },
        {
            code: "views.cached('aba', 'qweqwe')",
            errors: [{message: /should be wrapped/}],
            output: "views.cached('aba', function () {\n\treturn 'qweqwe';\n})"
        },
        {
            code: "views.cached('aba', 'qwe' + 'qwe')",
            errors: [{message: /should be wrapped/}],
            output: "views.cached('aba', function () {\n\treturn 'qwe' + 'qwe';\n})"
        },
        {
            code: "var t = 'qweqwe';\nviews.cached('aba', t)",
            errors: [{message: /should be wrapped/}]
        }
    ]

});
