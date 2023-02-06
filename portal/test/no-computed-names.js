const rule = require('../lib/no-computed-names'),
    RuleTester = require('eslint').RuleTester;

const ruleTester = new RuleTester({globals: {views: true}});

ruleTester.run('no-computed-names', rule, {
    valid: [
        {
            code: "views('abba', function () {})"
        },
        {
            code: "views.cached('abba', function () {})"
        },
        {
            code: `views('abba', function (data, req, execView) {
                execView('asd', data);
            })`
        },
        {
            code: `views('abba', function abba(data, req, execView) {
                execView(abba.base, data);
            })`
        },
        {
            code: `views('abba', function (data, req, execView) {
                execView(data.x ? 'asd' : 'eee', data);
            })`
        },
        {
            code: `views('abba', function (data, req, execView) {
                execView(data.x, data);
            })`
        },
        {
            code: `views.cached('abba', function (req, execView) {
                execView('asd', data);
            })`
        },
        {
            code: `views.cached('abba', function abba(req, execView) {
                execView(abba.base, data);
            })`
        },
        {
            code: "home.view('abba', {})"
        }
    ],

    invalid: [
        {
            code: "views('ab' + 'ba', function () {})",
            errors: [{message: /should be a string/}]
        },
        {
            code: `views('aba', function (data, req, execView) {
                var x = 42;
                execView('qwe' + 'x', data);
            })`,
            errors: [
                {message: /should be a string/}
            ]
        },
        {
            code: "views.cached('ab' + 'ba', function () {})",
            errors: [{message: /should be a string/}]
        },
        {
            code: `views.cached('aba', function (req, execView) {
                execView('qwe' + 'x', req);
            })`,
            errors: [
                {message: /should be a string/}
            ]
        },
        {
            code: "home.view('ab' + 'ba', {})",
            errors: [{message: /should be a string/}]
        }
    ]

});
