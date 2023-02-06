(function() {
    'use strict';

    var test = require('tap').test;
    var exec = require('child_process').exec;
    var fs = require('vow-fs');
    var rmdir = require('rimraf');
    var vow = require('vow');
    var path = require('path');

    var fileList0 = [
        'some.view.js',
        'ru.lang.json',
        'some.ru.view.js',
        'uk.lang.json',
        'some.uk.view.js',
        'desktop.view.js'
    ];

    var fileList1 = [
        'some.view.js',
        'ru.lang.json',
        'some.ru.view.js',
        'desktop.view.js'
    ];

    var fileList2 = [
        'some.view.js',
        'some2.view.js',
        'ru.lang.json',
        'some.ru.view.js',
        'some2.ru.view.js',
        'desktop.view.js'
    ];

    var fileList3 = [
        'some.view.js',
        'some2.view.js',
        'ru.lang.json',
        'some.ru.view.js',
        'some2.ru.view.js',
        'result.view.js'
    ];

    var fileList4 = [
        'some.view.js',
        'some2.view.js',
        'ru.lang.json',
        'uk.lang.json',
        'some.ru.view.js',
        'some2.ru.view.js',
        'some2.uk.view.js',
        'result.view.js'
    ];

    var fileList5 = [
        'some.view.js',
        'some.ru.view.js',
        'some.uk.view.js',
        'desktop.view.js'
    ];

    var fileList6 = [
        'some.view.js',
        'some.ru.view.js',
        'some.uk.view.js',
        'some2.view.js',
        'some2.ru.view.js',
        'some2.uk.view.js',
        'desktop.view.js'
    ];

    var fileList7 = [
        'ru.lang.json',
        'uk.lang.json',
        'some.view.js',
        'some.ru.view.js',
        'some.uk.view.js',
        'some2.view.js',
        'some2.ru.view.js',
        'some2.uk.view.js',
        'desktop.view.js'
    ];

    var langList0 = [
        'ru.lang.json',
        'uk.lang.json'
    ];

    function clear(test) {
        rmdir.sync(test + '/result');
    }

    function compareFiles(t, testName, fileList, alt) {
        var promises = [],
            fail = t.fail.bind(t);
        fileList.forEach(function(fileName) {
            var defer = vow.defer(),
                actual,
                shouldbe,
                shouldbe2,
                promises2 = [];

            if (alt) {
                promises2.push(fs.read(testName + '/shouldbe2/' + fileName).then(function(data) {
                    shouldbe2 = data.toString();
                }, fail));
            }

            promises.push(defer.promise());
            vow.all(promises2.concat([fs.read(testName + '/result/' + fileName).then(function(data) {
                actual = data.toString();
            }, fail), fs.read(testName + '/shouldbe/' + fileName).then(function(data) {
                shouldbe = data.toString();
            }, fail)])).then(function() {
                if (alt && actual === shouldbe2) {
                    t.equal(actual, shouldbe2, testName + ': ' + fileName + ' contents');
                } else {
                    t.equal(actual, shouldbe, testName + ': ' + fileName + ' contents');
                }
                defer.resolve();
            });
        });
        return vow.all(promises);
    }

    function checkNotExists (t, testName, fileList) {
        return vow.all(fileList.map(function (fileName) {
            return fs.exists(testName + '/result/' + fileName).then(function (exists) {
                t.equal(exists, false, testName + ': ' + fileName + ' should not exists');
            });
        }));
    }

    function checkStderr (t, stderr, should, hint) {
        if (stderr) {
            t.equal(stderr.split('\n')[0], should, hint);
        } else {
            t.fail('No stderr');
        }
    }

    test('normal test', function(t) {
        t.plan(fileList0.length);
        clear('test0');
        exec('node ../run.js --config=./test0/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test0', fileList0).then(function() {
                t.end();
            });
        });
    });

    test('unknown lang key', function(t) {
        t.plan(1);
        clear('test1');
        exec('node ../run.js --config=./test1/config.json --force', function(error, stdout, stderr) {
            if (error) {
                checkStderr(t, stderr, 'Error: Cannot find string text in lang ru', 'lang.json must contains proper string');
            } else {
                t.fail('Should be error here');
            }
            t.end();
        });
    });

    test('unknown lang dynamic node', function(t) {
        t.plan(1);
        clear('test2');
        exec('node ../run.js --config=./test2/config.json --force', function(error, stdout, stderr) {
            if (error) {
                checkStderr(t, stderr, 'Error: Cannot find node level0.level1 in lang ru', 'lang.json must contains subpath from .l10n()')
            } else {
                t.fail('Should be error here');
            }
            t.end();
        });
    });

    test('array of strings', function(t) {
        t.plan(fileList1.length);
        clear('test3');
        exec('node ../run.js --config=./test3/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test3', fileList1).then(function() {
                t.end();
            });
        });
    });

    test('incorrect usage of the strings array', function(t) {
        t.plan(1);
        clear('test4');
        exec('node ../run.js --config=./test4/config.json --force', function(error, stdout, stderr) {
            if (error) {
                checkStderr(t, stderr, 'Error: Lang value for key array should be string in lang ru', 'Expected string, but array found');
            } else {
                t.fail('Should be error here');
            }
            t.end();
        });
    });

    test('Array normal usage', function(t) {
        t.plan(fileList1.length);
        clear('test5');
        exec('node ../run.js --config=./test5/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test5', fileList1).then(function() {
                t.end();
            });
        });
    });

    test('Multiple levels', function(t) {
        t.plan(fileList2.length);
        clear('test6');
        exec('node ../run.js --config=./test6/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test6', fileList2).then(function() {
                t.end();
            });
        });
    });

    test('Multiple pages', function(t) {
        t.plan(fileList1.length);
        clear('test7');
        exec('node ../run.js --config=./test7/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test7', fileList1, true).then(function() {
                t.end();
            });
        });
    });

    test('Complex l10n usage', function(t) {
        t.plan(fileList1.length);
        clear('test8');
        exec('node ../run.js --config=./test8/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test8', fileList1).then(function() {
                t.end();
            });
        });
    });

    test('Bad escaping \\r\\n', function(t) {
        t.plan(fileList1.length);
        clear('test9');
        exec('node ../run.js --config=./test9/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test9', fileList1).then(function() {
                t.end();
            });
        });
    });

    test('Dynamic l10n usage another test', function(t) {
        t.plan(fileList1.length);
        clear('test10');
        exec('node ../run.js --config=./test10/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test10', fileList1).then(function() {
                t.end();
            });
        });
    });

    test('<folder> usage', function(t) {
        t.plan(fileList1.length);
        clear('test11');
        exec('node ../run.js --config=./test11/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test11', fileList1).then(function() {
                t.end();
            });
        });
    });

    test('common lang list usage', function(t) {
        t.plan(fileList0.length);
        clear('test13');
        exec('node ../run.js --config=./test13/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test13', fileList0).then(function() {
                t.end();
            });
        });
    });

    test('quot type detection', function(t) {
        t.plan(fileList0.length);
        clear('test14');
        exec('node ../run.js --config=./test14/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test14', fileList0).then(function() {
                t.end();
            });
        });
    });

    test('quot type detection 2', function(t) {
        t.plan(fileList0.length);
        clear('test15');
        exec('node ../run.js --config=./test15/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test15', fileList0).then(function() {
                t.end();
            });
        });
    });

    test('INCLUDE in comment', function(t) {
        t.plan(fileList0.length);
        clear('test16');
        exec('node ../run.js --config=./test16/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test16', fileList0).then(function() {
                t.end();
            });
        });
    });

    test('multiline template', function(t) {
        t.plan(fileList0.length);
        clear('test17');
        exec('node ../run.js --config=./test17/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test17', fileList0).then(function() {
                t.end();
            });
        });
    });

    test('INCLUDE WATCH', function(t) {
        t.plan(fileList0.length);
        clear('test18');
        exec('node ../run.js --config=./test18/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test18', fileList0).then(function() {
                t.end();
            });
        });
    });

    test('RAWINC WATCH', function(t) {
        t.plan(fileList0.length);
        clear('test19');
        exec('node ../run.js --config=./test19/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test19', fileList0).then(function() {
                t.end();
            });
        });
    });

    test('viewMask usage', function(t) {
        t.plan(fileList3.length);
        clear('test20');
        exec('node ../run.js --config=./test20/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test20', fileList3).then(function() {
                t.end();
            });
        });
    });

    test('exclude level', function(t) {
        t.plan(fileList3.length);
        clear('test21');
        exec('node ../run.js --config=./test21/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test21', fileList3).then(function() {
                t.end();
            });
        });
    });

    test('Object in lang', function(t) {
        t.plan(fileList0.length);
        clear('test22');
        exec('node ../run.js --config=./test22/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test22', fileList0).then(function() {
                t.end();
            });
        });
    });

    test('langList in levels', function(t) {
        t.plan(fileList4.length);
        clear('test23');
        exec('node ../run.js --config=./test23/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test23', fileList4).then(function() {
                t.end();
            });
        });
    });

    test('view by mask not found', function(t) {
        t.plan(1);
        clear('test25');
        exec('node ../run.js --config=./test25/config.json --force', function(error, stdout, stderr) {
            if (error) {
                checkStderr(t, stderr, 'Error: View files not found', 'At least one view must be found');
            } else {
                t.fail('Should be error here');
            }
            t.end();
        });
    });

    test('requiredTranslations option', function(t) {
        t.plan(fileList0.length);
        clear('test26');
        exec('node ../run.js --config=./test26/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'test26', fileList0).then(function() {
                t.end();
            });
        });
    });

    test('writeRequiredLang: false option', function(t) {
        t.plan(fileList5.length + langList0.length);
        clear('writeRequiredLang-option');
        exec('node ../run.js --config=./writeRequiredLang-option/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'writeRequiredLang-option', fileList5).then(function() {
                return checkNotExists(t, 'writeRequiredLang-option', langList0);
            }).always(function () {
                t.end();
            });
        });
    });

    test('acornOptions: es6 ok', function(t) {
        t.plan(fileList5.length);
        clear('es6-ok');
        exec('node ../run.js --config=./es6-ok/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'es6-ok', fileList5).always(function() {
                t.end();
            });
        });
    });

    test('acornOptions: es6 fail', function(t) {
        t.plan(1);
        clear('es6-fail');
        exec('node ../run.js --config=./es6-fail/config.json', function(error, stdout, stderr) {
            if (error) {
                checkStderr(t, stderr, 'SyntaxError: Unexpected token (7:21)', 'ecma5 not compatible code');
            } else {
                t.fail('Should be error here');
            }
            t.end();
        });
    });

    test('missing lang', function(t) {
        t.plan(1);
        clear('missing-lang');
        exec('node ../run.js --config=./missing-lang/config.json', function(error, stdout, stderr) {
            var expected = 'Error: ENOENT: no such file or directory';

            if (error) {
                t.equal(stderr.slice(0, expected.length), expected, 'should fail if lang is not exists');
            } else {
                t.fail('Should be error here');
            }
            t.end();
        });
    });

    test('full run in api', function(t) {
        t.plan(fileList5.length);
        clear('api-run');
        exec('node api-run/run.js', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'api-run', fileList5).always(function() {
                t.end();
            });
        });
    });

    test('full run in api with error', function(t) {
        t.plan(1);
        clear('api-fail');
        exec('node api-fail/run.js', function(error, stdout, stderr) {
            if (error) {
                var expected = 'ENOENT: no such file or directory';
                t.equal(stderr.slice(0, expected.length), expected, 'File not found');
            } else {
                t.fail('Should be error here');
            }
            t.end();
        });
    });

    test('basic transforms usage', function(t) {
        t.plan(fileList5.length);
        clear('transforms-simple');
        exec('node transforms-simple/run.js', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'transforms-simple', fileList5).always(function() {
                t.end();
            });
        });
    });

    test('error from transforms catch', function(t) {
        t.plan(1);
        clear('transforms-error');
        exec('node transforms-error/run.js', function(error, stdout, stderr) {
            if (error) {
                checkStderr(t, stderr, 'TransformError');
            } else {
                t.fail('Should be error here');
            }
            t.end();
        });
    });

    test('transforms with options', function(t) {
        t.plan(fileList5.length);
        clear('transforms-opts');
        exec('node transforms-opts/run.js', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'transforms-opts', fileList5).always(function() {
                t.end();
            });
        });
    });

    test('transforms with promise', function(t) {
        t.plan(fileList5.length);
        clear('transforms-promise');
        exec('node transforms-promise/run.js', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'transforms-promise', fileList5).always(function() {
                t.end();
            });
        });
    });

    test('error from transform promise', function(t) {
        t.plan(1);
        clear('transforms-promise-error');
        exec('node transforms-promise-error/run.js', function(error, stdout, stderr) {
            if (error) {
                checkStderr(t, stderr, 'Transform with promise error');
            } else {
                t.fail('Should be error here');
            }
            t.end();
        });
    });

    test('multiple transforms', function(t) {
        t.plan(fileList5.length);
        clear('transforms-multiple');
        exec('node transforms-multiple/run.js', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'transforms-multiple', fileList5).always(function() {
                t.end();
            });
        });
    });

    test('transforms with view per file', function(t) {
        t.plan(fileList5.length);
        clear('transforms-views-per-file');
        exec('node transforms-views-per-file/run.js', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'transforms-views-per-file', fileList5).always(function() {
                t.end();
            });
        });
    });

    test('api run with rawinc', function(t) {
        t.plan(fileList5.length);
        clear('api-rawinc-deps');
        exec('node api-rawinc-deps/run.js', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'api-rawinc-deps', fileList5).always(function() {
                t.end();
            });
        });
    });

    test('transforms in json config by require', function(t) {
        t.plan(fileList5.length);
        clear('transforms-require');
        exec('node ../run.js --config=./transforms-require/config.json', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'transforms-require', fileList5).always(function() {
                t.end();
            });
        });
    });

    test('api with rootDir option', function(t) {
        t.plan(fileList5.length);
        clear('api-root-dir');
        exec('node api-root-dir/run.js', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'api-root-dir', fileList5).always(function() {
                t.end();
            });
        });
    });

    test('api run with incorrect path', function(t) {
        t.plan(1);
        clear('api-root-missing-files');
        exec('node api-root-missing-files/run.js', function(error, stdout, stderr) {
            if (error) {
                checkStderr(t, stderr, '[Error: No view files found!]');
            } else {
                t.fail('Should be error here');
            }
            t.end();
        });
    });

    test('api run with incorrect path', function(t) {
        t.plan(1);
        clear('api-root-missing-files');
        exec('node api-root-missing-include/run.js', function(error, stdout, stderr) {
            if (error) {
                t.equal(stderr.trim(),
                    '[Error: File ' + path.resolve('api-root-missing-include/blocks/test.js') + ' in INCLUDE call not found!]',
                    'include miss');
            } else {
                t.fail('Should be error here');
            }
            t.end();
        });
    });

    test('api without command option', function(t) {
        t.plan(fileList5.length);
        clear('api-no-command');
        exec('node api-no-command/run.js', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'api-no-command', fileList5).always(function() {
                t.end();
            });
        });
    });

    test('api usage with filtered views and execView rename', function(t) {
        t.plan(fileList5.length);
        clear('api-unneeded-includes');
        exec('node api-unneeded-includes/run.js', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'api-unneeded-includes', fileList5).always(function() {
                t.end();
            });
        });
    });

    test('api usage with default options', function(t) {
        t.plan(fileList5.length);
        clear('output-default-options');
        exec('node output-default-options/run.js', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'output-default-options', fileList5).always(function() {
                t.end();
            });
        });
    });

    test('api usage with watch option', function(t) {
        t.plan(fileList5.length);
        clear('output-with-watch');
        exec('node output-with-watch/run.js', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'output-with-watch', fileList5).always(function() {
                t.end();
            });
        });
    });

    test('api usage without localization', function(t) {
        t.plan(fileList6.length);
        clear('output-without-localization');
        exec('node output-without-localization/run.js', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'output-without-localization', fileList6).always(function() {
                t.end();
            });
        });
    });

    test('api usage with full options', function(t) {
        t.plan(fileList7.length);
        clear('output-full-options');
        exec('node output-full-options/run.js', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'output-full-options', fileList7).always(function() {
                t.end();
            });
        });
    });

    test('api usage with extra escaping in translation', function(t) {
        t.plan(fileList5.length);
        clear('escaped-str');
        exec('node escaped-str/run.js', function(error, stdout, stderr) {
            if (error) {
                t.fail(error);
            }
            if (stderr) {
                t.fail(stderr);
            }
            compareFiles(t, 'escaped-str', fileList5).always(function() {
                t.end();
            });
        });
    });

})();
