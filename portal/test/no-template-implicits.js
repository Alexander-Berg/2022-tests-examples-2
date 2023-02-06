const rule = require('../lib/no-template-implicits');
const RuleTester = require('eslint').RuleTester;

const ruleTester = new RuleTester({
    parser: require.resolve('morda-template-eslint-parser'),
    parserOptions: {html: true}
});

ruleTester.run('no-template-implicits', rule, {
    valid: [{code: '[%data:test%]'}],
    invalid: [
        {
            code: '<span>[% noSource %]</span>',
            errors: [{message: /^Источник не указан/}]
        },
        {
            code: '<span>[% invalid:test %]</span>',
            errors: [{message: /invalid не валиден/}]
        }
    ]
});
