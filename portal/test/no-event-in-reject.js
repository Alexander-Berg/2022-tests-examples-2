const rule = require('../lib/no-event-in-reject'),
    RuleTester = require('eslint').RuleTester;

const ruleTester = new RuleTester({
    parserOptions: {
        ecmaVersion: 2018
    },
    globals: {Promise: true}
});

ruleTester.run('no-event-in-reject', rule, {
    valid: [
        {
            code: `var x = new Promise(function (x) {
                (new Image()).onload = x;
            });`
        },
        {
            code: `var x = new Ololo((x, b) => {
                (new Image).onload = b;
            });`
        },
        {
            code: `var Promise = '123';
            var x = new Promise((x, b) => {
                x.onerror = b;
            });`
        },
        {
            code: `var x = new Promise((x, b) => {
                x['on' + qq] = b;
            });`
        },
        {
            code: `var x = new Promise((x, b) => {
                m.addEventListener('error', am);
            });`
        }
    ],

    invalid: [
        {
            code: `var x = new Promise((x, m) => {
                (new Image).onerror = m;
            })`,
            errors: [{message: 'Promise should be rejected with Error object, not Event'}]
        },
        {
            code: `var x = new Promise(function (x, m) {
                (new Image).onerror = m;
            })`,
            errors: [{message: 'Promise should be rejected with Error object, not Event'}]
        },
        {
            code: `var x = new Promise(function (x, m) {
                (new Image).onerror = m;
            })`,
            errors: [{message: 'Promise should be rejected with Error object, not Event'}]
        },
        {
            code: `var x = new Promise(function (x, m) {
                q.addEventListener('qweqwe', m);
            })`,
            errors: [{message: 'Promise should be rejected with Error object, not Event'}]
        },
        {
            code: `var x = new Promise(function (x, m) {
                addEventListener('qweqwe', m);
            })`,
            errors: [{message: 'Promise should be rejected with Error object, not Event'}]
        }
    ]

});
