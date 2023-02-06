'use strict';

const rule = require('../../../lib/rules/no-toplevel-i18n-calls');
const { ruleTester } = require('../tester');

const onFail = (code) => {
  return {
    code,
    errors: [{ message: 'Top level `i18n` call is forbidden, wrap it in function call' }],
  };
};

ruleTester.run('no-toplevel-i18n-calls', rule, {
  valid: [
    `import { i18n } from './Blah.i18n'; function blah() { i18n('this is fine') }`,
    `import { i18n } from './Blah.i18n'; const a = function() { i18n('this is fine') }`,
    `import { i18n } from './Blah.i18n'; const b = () => { i18n('this is fine')}`,
    `import { i18n } from './Blah.i18n'; const blah = { a: () => i18n('this is fine') }`,
    `import { i18nRaw } from './Blah.i18n'; function blah() { i18nRaw('this is fine') }`,
  ],

  invalid: [
    `import { i18n } from './Blah.i18n'; i18n('fail')`,
    `import { i18n } from './Blah.i18n'; const blah = i18n('fail')`,
    `import { i18n } from './Blah.i18n'; const blah = { a: i18n('fail') }`,
    `import { i18nRaw } from './Blah.i18n'; i18nRaw('fail')`,
    `import { i18nRaw } from './Blah.i18n'; const blah = i18nRaw('fail')`,
    `import { i18nRaw } from './Blah.i18n'; const blah = { a: i18nRaw('fail') }`,
  ].map(onFail),
});
