const rule = require('../lib/no-nested-views'),
    RuleTester = require('eslint').RuleTester;

function wrap(cases) {
    var res = [];
    cases.forEach(code => {
        res.push(code);
        res.push(`(function () {
            ${code}
        })();`);
        res.push(`(function (views) {
            ${code}
        })(views);`);
    });
    return res;
}

const ruleTester = new RuleTester({globals: {views: true}});
const valid = wrap([
        "views('abba', function () {})",
        `(function () {
            views('abba', function () {});
        })()`,
        `views('abba', function (data, req, execView) {
            execView('asd', data);
        })`,
        `function xxxx() {
            function views () {};
            views('abba', function () {});
        }`,
        `function views () {}
        function xxxx() {
            views('abba', function () {});
        }`,
        "views.cached('abba', function () {})",
        `views.cached('abba', function (req, execView) {
            execView('asd', req);
        })`,
        `function xxxx() {
            function views () {};
            views.cached('abba', function () {});
        }`
    ]),
    invalid = wrap([
        `views('abba', function () {
            views('eee', function () {});
        })`,
        `function xxxx() {
            views('abba', function () {});
        }`,
        `function xxxx() {
            views.cached('abba', function () {});
        }`,
        `function xx() {
            views('eee', function () {});
        }
        views('aba', function (data, req, execView) {
            xx();
        })`,
        `views('abba', function () {
            views.cached('eee', function () {});
        })`,
        `views.cached('abba', function () {
            views('eee', function () {});
        })`,
        `function xx() {
            views.cached('eee', function () {});
        }
        views('aba', function (data, req, execView) {
            xx();
        })`

    ]);

ruleTester.run('no-nested-views', rule, {
    valid: valid.map(code => ({code})),

    invalid: invalid.map(code => ({
        code,
        errors: [{message: 'Template must be declared on top level'}]
    }))

});
