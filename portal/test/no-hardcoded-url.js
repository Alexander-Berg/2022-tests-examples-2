const rule = require('../lib/no-hardcoded-url');
const RuleTester = require('eslint').RuleTester;

const ruleTester = new RuleTester({
    env: {es6: true}
});

ruleTester.run('no-hardcoded-url', rule, {
    valid: [
        {
            code: 'var t = "https://valid.site";',
            options: [
                {
                    urls: ['https://evil.com']
                }
            ]
        }
    ],
    invalid: [
        {
            code: 'var t = "https://evil.com";',
            options: [
                {
                    urls: ['https://evil.com']
                }
            ],
            errors: [{message: /evil.com/}]
        },
        {
            code: 'var t = `https://evil.com{path}`;',
            options: [
                {
                    urls: ['https://evil.com']
                }
            ],
            errors: [{message: /evil.com/}]
        }
    ]
});
