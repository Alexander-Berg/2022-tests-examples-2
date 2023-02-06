'use strict';

// disable "colors"
process.argv.push('--no-color');
require('colors');

var tap = require('tap');
var test = tap.test;
var vow = require('vow');
var rapidoLang = require('../run');

test('calcRequiredKeys', function(t) {
    t.deepEqual(rapidoLang.calcRequiredKeys('a.l10n("b")'), ["b"], "simple usage");
    t.deepEqual(rapidoLang.calcRequiredKeys('a.l10n(\'b\')'), ["b"], "other parenthesis");
    t.deepEqual(rapidoLang.calcRequiredKeys('a.l10n("b.c")'), ["b.c"], "subkey");
    t.deepEqual(rapidoLang.calcRequiredKeys('a.l10n("b.c");a.l10n("d")'), ["b.c", "d"], "multiple keys");
    t.deepEqual(rapidoLang.calcRequiredKeys('a.l10n("b.c");a.l10n(\'d\')'), ["b.c", "d"], "multiple keys with different parenthesis");
    t.deepEqual(rapidoLang.calcRequiredKeys('a.l10n("b." + c)'), ["b"], "dynamic key 0");
    t.deepEqual(rapidoLang.calcRequiredKeys('a.l10n("b" + c)'), [], "dynamic key 1");
    t.deepEqual(rapidoLang.calcRequiredKeys('a.l10n("b.c" + d)'), ["b"], "dynamic key 2");
    t.deepEqual(rapidoLang.calcRequiredKeys('a.l10n("b.c." + d)'), ["b.c"], "dynamic key 3");
    t.deepEqual(rapidoLang.calcRequiredKeys('a.l10n(c)'), [], "dynamic key 4");

    t.end();
});

test('inlineLangKeys', function (t) {
    t.plan(3);

    var langData = {
        test: 'val'
    };

    t.equal(rapidoLang.inlineLangKeys(langData, 'ru', 'test.js', '"[% l10n:test %]"'), '"val"', "simple usage");
    t.equal(rapidoLang.inlineLangKeys(langData, 'ru', 'test.js', '"[% test %]"'), '"[% test %]"', "simple usage 2");
    try {
        rapidoLang.inlineLangKeys(langData, 'ru', 'test.js', '"[% l10n:test2 %]"');
    } catch (err) {
        t.equal(err.message, 'Cannot find string test2 in lang ru', 'unknown error');
    }

    t.end();
});

test('ecmaVersion', function (t) {
    t.plan(4);

    var langData = {
        test: 'val'
    };

    rapidoLang.acornSetup({ecmaVersion: 5});
    t.equal(rapidoLang.inlineLangKeys(langData, 'ru', 'test.js',
        '(function() {return this.l10n("test");})'
    ),
        '(function() {return \'val\';})',
        "simple es5 usage"
    );
    try {
        rapidoLang.inlineLangKeys(langData, 'ru', 'test.js', '(() => this.l10n("test"))');
    } catch (err) {
        t.equal(err.message, 'Unexpected token (1:2)', 'es6 arrow functions is not allowed in es5');
    }

    rapidoLang.acornSetup({ecmaVersion: 6});
    t.equal(rapidoLang.inlineLangKeys(langData, 'ru', 'test.js',
        '(function() {return this.l10n("test");})'
        ),
        '(function() {return \'val\';})',
        "simple es5 usage"
    );
    t.equal(rapidoLang.inlineLangKeys(langData, 'ru', 'test.js',
        '(() => this.l10n("test"))'
    ),
        '(() => \'val\')',
        "simple es6 usage"
    );

    t.end();
});

test('applyTransforms', function (t) {
    t.plan(4);

    var transformsPack = [
        {
            desc: 'simple transforms',
            transforms: [
                function (fileName, contents) {
                    return fileName + ':' + contents;
                }
            ],
            expected: 'file.js:contents'
        },
        {
            desc: 'async transforms',
            transforms: [
                function (fileName, contents) {
                    return fileName + ':' + contents;
                },
                function (fileName, contents) {
                    var defer = vow.defer();

                    setTimeout(function () {
                        defer.resolve(contents + ':' + 10);
                    }, 10);

                    return defer.promise();
                }
            ],
            expected: 'file.js:contents:10'
        },
        {
            desc: 'transforms order',
            transforms: [
                function (fileName, contents) {
                    return fileName + ':' + contents;
                },
                function (fileName, contents) {
                    if (contents.indexOf(fileName) > -1) {
                        return 'second';
                    } else {
                        return 'first';
                    }
                }
            ],
            expected: 'second'
        },
        {
            desc: 'async transforms 2',
            transforms: [
                function (fileName, contents) {
                    return 'first';
                },
                function (fileName, contents) {
                    var defer = vow.defer();

                    setTimeout(function () {
                        defer.resolve(contents + ':' + 10);
                    }, 10);

                    return defer.promise();
                },
                function (fileName, contents) {
                    var defer = vow.defer();

                    setTimeout(function () {
                        defer.resolve(contents + ':' + 20);
                    }, 20);

                    return defer.promise();
                },
                function (fileName, contents) {
                    return contents + ':forth'
                }
            ],
            expected: 'first:10:20:forth'
        }
    ];

    return vow.all(transformsPack.map(function (test) {
        return rapidoLang.applyTransforms('file.js', 'contents', test.transforms).then(function (transformed) {
            t.equal(transformed, test.expected, test.desc);
        });
    })).always(function () {
        t.end();
    })
}).catch(tap.threw);
