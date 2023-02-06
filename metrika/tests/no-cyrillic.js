'use strict';

let rule = require('../rules/no-cyrillic');
let RuleTester = require('eslint').RuleTester;

let ruleTester = new RuleTester();

const errorText = 'Cyrillic symbols should not be used in the code';

ruleTester.run('no-cyrillic', rule, {
    invalid: [
        {
            code: '"Кнопка"',
            errors: [
                {
                    message: errorText,
                },
            ],
        },
        {
            code: '"some Ё!"',
            errors: [
                {
                    message: errorText,
                    type: 'Literal',
                },
            ],
        },
        {
            code: "'just сообщение english'",
            errors: [
                {
                    message: errorText,
                    type: 'Literal',
                },
            ],
        },
        {
            code: '`Шаблон`',
            parserOptions: {
                ecmaVersion: 6,
            },
            errors: [
                {
                    message: errorText,
                    type: 'TemplateElement',
                },
            ],
        },
        {
            code: '<div>текст</div>',
            parserOptions: {
                ecmaVersion: 6,
                ecmaFeatures: {
                    jsx: true,
                },
            },
            errors: [
                {
                    message: errorText,
                    type: 'JSXText',
                },
            ],
        },
        {
            code: '<div>русский<b>text</b></div>',
            parserOptions: {
                ecmaVersion: 6,
                ecmaFeatures: {
                    jsx: true,
                },
            },
            errors: [
                {
                    message: errorText,
                    type: 'JSXText',
                },
            ],
        },
        {
            code: "<input placeholder='текст'/>",
            parserOptions: {
                ecmaVersion: 6,
                ecmaFeatures: {
                    jsx: true,
                },
            },
            errors: [
                {
                    message: errorText,
                    type: 'Literal',
                },
            ],
        },
        {
            code: '<div><b>слово</b></div>',
            parserOptions: {
                ecmaVersion: 6,
                ecmaFeatures: {
                    jsx: true,
                },
            },
            errors: [
                {
                    message: errorText,
                    type: 'JSXText',
                },
            ],
        },
        {
            code: "let word = 'операция';",
            parserOptions: {
                ecmaVersion: 6,
            },
            errors: [
                {
                    message: errorText,
                    type: 'Literal',
                },
            ],
        },
        {
            code: "function i17n(value) { return value; }; i17n('деньги') ",
            errors: [
                {
                    message: errorText,
                    type: 'Literal',
                },
            ],
        },
        {
            code: "console.log('привет')",
            errors: [
                {
                    message: errorText,
                    type: 'Literal',
                },
            ],
        },
    ],

    valid: [
        '"button"',
        '1',
        {
            code: '`template`',
            parserOptions: {
                ecmaVersion: 6,
            },
        },
        {
            code: "function i18n(value) { return value; }; i18n('русская жизнь')",
        },
        {
            code: "function i18n(value) { return value; }; i18n(`шаблонная строка`)",
        },
        {
            code: '// комментарий',
        },
        {
            code: '/* сложный комментарий */',
        },
        {
            code: "function i18n(value) { return value; }; const text = (<div>{i18n('русские слова')}</div>);",
            parserOptions: {
                ecmaVersion: 6,
                ecmaFeatures: {
                    jsx: true,
                },
            },
        },
    ],
});
