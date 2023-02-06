/* global should */
/* eslint no-eval: 1, dot-notation: 1, no-unused-expressions: 0 */
describe('home.settingsJs', function() {
    var settingsJs = home.settingsJs;

    // Mock thirdParty
    var mock = {};
    mock.push = function (data) {
        try {
            var window = {home: {}};
            eval(data); // jshint ignore:line
            mock.data = window.home.export;
        } catch (e) {
            mock.data = {error: e.message};
        }
    };
    mock.unshift = mock.push;

    mock.get = function () {
        var data = mock.data;
        delete mock.data;
        return data;
    };

    describe('serverside', function() {
        it('добавляет в общий неймспейс', function() {
            var sjs = settingsJs(mock);
            sjs.has('test').should.be.false;

            sjs.add('test', 123);
            sjs.has('test').should.be.true;

            sjs.renderAllVars();

            mock.get().should.deep.equal({
                common: {
                    test: 123
                }
            });
        });

        it('не добавляет undefined', function() {
            var sjs = settingsJs(mock);
            sjs.add('test');
            sjs.renderAllVars();

            mock.get().should.deep.equal({});
        });

        it('добавляет 0', function() {
            var sjs = settingsJs(mock);
            sjs.add('test', 0);
            sjs.renderAllVars();

            mock.get().should.deep.equal({
                common: {
                    test: 0
                }
            });
        });

        it('добавляет false', function() {
            var sjs = settingsJs(mock);
            sjs.add('test', false);
            sjs.renderAllVars();

            mock.get().should.deep.equal({
                common: {
                    test: false
                }
            });
        });

        it('добавляет и в указанный, и в общий неймспейс', function() {
            var sjs = settingsJs(mock);
            sjs.has('test').should.be.false;

            sjs.has('test', 'namespace2').should.be.false;

            sjs.add('test', 123);
            sjs.has('test').should.be.true;

            sjs.has('test', 'namespace2').should.be.false;

            sjs.add('test', 'hello', 'namespace2');
            sjs.has('test').should.be.true;

            sjs.has('test', 'namespace2').should.be.true;

            sjs.renderAllVars();

            mock.get().should.deep.equal({
                common: {
                    test: 123
                },
                namespace2: {
                    test: 'hello'
                }
            });
        });

        it('мёржит последовательные использования add', function () {
            var sjs = settingsJs(mock);

            sjs.add('data', {
                key0: 1,
                key1: 2
            }, 'ns');

            sjs.add('data', {
                key1: 3,
                key2: 4
            }, 'ns');

            sjs.add('data.key3', 5, 'ns');

            sjs.add('dup', 'val', 'ns');
            sjs.add('dup', 'val', 'ns');

            sjs.renderAllVars();

            mock.get().should.deep.equal({
                ns: {
                    data: {
                        key0: 1,
                        key1: 3,
                        key2: 4,
                        key3: 5
                    },
                    dup: 'val'
                }
            });
        });

        it('экранирует теги', function () {
            var sjs = settingsJs(mock);

            sjs.add('data', {
                key0: '<script>alert(document.cookie)</script>',
                key1: '<a href="a.b?x&q">multi\u2028line\u2029string</a>'
            }, 'ns');

            sjs.getRawScript().should.not.include('<script>');
            sjs.getRawScript().should.not.include('\u2028');
            sjs.getRawScript().should.not.include('\u2029');

            sjs.renderAllVars();

            mock.get().should.deep.equal({
                ns: {
                    data: {
                        key0: '<script>alert(document.cookie)</script>',
                        key1: '<a href="a.b?x&q">multi\u2028line\u2029string</a>'
                    }
                }
            });
        });
    });

    describe('clientside', function() {
        var testVar1 = 'A',
            testVar2 = 22,
            testVar3 = {},
            testVar4 = 'test4';
        before(function() {
            home.export = {
                testA: testVar1,
                testB: {
                    testB2: testVar2,
                    other: null
                },
                testC: {
                    testC2: {
                        testC3: testVar3,
                        testC2: 'Y',
                        other: null
                    },
                    other: null
                },
                other: null
            };
        });

        it('получает значения', function() {
            home.getData('testA').should.equal(testVar1);
            home.getData('testB.testB2').should.equal(testVar2);
            home.getData('testC.testC2.testC3').should.equal(testVar3);
            should.not.exist(home.getData('testC.testC2.testC3.wrongParam'));
        });

        it('получает значения c дефолтами', function() {
            home.getData('testA', 'test1').should.equal(testVar1);
            home.getData('testB.testB2', 'test2').should.equal(testVar2);
            home.getData('testC.testC2.testC3', 'test3').should.equal(testVar3);
            home.getData('testC.testC2.testC3.wrongParam', testVar4).should.equal(testVar4);
        });
    });
});

