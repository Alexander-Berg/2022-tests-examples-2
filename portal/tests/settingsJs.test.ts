import { settingsJs } from '../settingsJs';
import { getData } from '../getClientData';

function getVars(script: string) {
    // eslint-disable-next-line no-eval
    eval(script);
    return window.home.export;
}

describe('settingsJs', () => {
    describe('serverside', () => {
        test('добавляет в общий неймспейс', () => {
            let sjs = settingsJs();
            expect(sjs.has('test')).toEqual(false);

            sjs.add('test', 123);
            expect(sjs.has('test')).toEqual(true);

            expect(getVars(sjs.getRawScript())).toEqual({
                common: {
                    test: 123
                }
            });
        });

        test('не добавляет undefined', () => {
            let sjs = settingsJs();
            // @ts-expect-error undefined будет игнорироваться
            sjs.add('test', undefined);

            expect(getVars(sjs.getRawScript())).toEqual({});
        });

        test('добавляет 0', () => {
            let sjs = settingsJs();
            sjs.add('test', 0);

            expect(getVars(sjs.getRawScript())).toEqual({
                common: {
                    test: 0
                }
            });
        });

        test('добавляет false', () => {
            let sjs = settingsJs();
            sjs.add('test', false);

            expect(getVars(sjs.getRawScript())).toEqual({
                common: {
                    test: false
                }
            });
        });

        test('добавляет и в указанный, и в общий неймспейс', () => {
            let sjs = settingsJs();
            expect(sjs.has('test')).toEqual(false);

            expect(sjs.has('test', 'namespace2')).toEqual(false);

            sjs.add('test', 123);
            expect(sjs.has('test')).toEqual(true);

            expect(sjs.has('test', 'namespace2')).toEqual(false);

            sjs.add('test', 'hello', 'namespace2');
            expect(sjs.has('test')).toEqual(true);

            expect(sjs.has('test', 'namespace2')).toEqual(true);

            expect(getVars(sjs.getRawScript())).toEqual({
                common: {
                    test: 123
                },
                namespace2: {
                    test: 'hello'
                }
            });
        });

        test('мёржит последовательные использования add', () => {
            let sjs = settingsJs();

            sjs.add('data', {
                key0: 1,
                key1: 2
            }, 'ns');

            sjs.add('data', {
                key1: 3,
                key2: 4
            }, 'ns');

            sjs.add('data.key3', 5, 'ns');

            expect(getVars(sjs.getRawScript())).toEqual({
                ns: {
                    data: {
                        key0: 1,
                        key1: 3,
                        key2: 4,
                        key3: 5
                    }
                }
            });
        });

        test('экранирует теги', () => {
            let sjs = settingsJs();

            sjs.add('data', {
                key0: '<script>alert(document.cookie)</script>',
                key1: '<a href="a.b?x&q">multi\u2028line\u2029string</a>'
            }, 'ns');

            expect(sjs.getRawScript()).not.toContain('<script>');
            expect(sjs.getRawScript()).not.toContain('\u2028');
            expect(sjs.getRawScript()).not.toContain('\u2029');

            expect(getVars(sjs.getRawScript())).toEqual({
                ns: {
                    data: {
                        key0: '<script>alert(document.cookie)</script>',
                        key1: '<a href="a.b?x&q">multi\u2028line\u2029string</a>'
                    }
                }
            });
        });

        it('добавляет partial данные', () => {
            let sjs = settingsJs();
            sjs.addPartial('qwe', {
                key0: 1,
                key2: false
            }, 'p0');
            sjs.addPartial('qwe', {
                key0: 1,
                key2: false
            }, 'p1');
            sjs.addPartial('qwo', {
                key0: 42,
            }, 'p1');
            expect(sjs.getPartials()).toMatchSnapshot();
        });

        it('не дублирует данные при нескольких вызовах getPartials', () => {
            let sjs = settingsJs();
            sjs.addPartial('qwe', {
                key0: 1,
                key2: false
            }, 'p0');
            sjs.addPartial('qwe', {
                key0: 1,
                key2: false
            }, 'p1');
            sjs.addPartial('qwo', {
                key0: 42,
            }, 'p1');
            expect(sjs.getPartials()).toMatchSnapshot();

            expect(sjs.getPartials()).toEqual('');

            sjs.addPartial('asd', 42, 'px');
            expect(sjs.getPartials()).toMatchSnapshot();
        });
    });

    describe('clientside', () => {
        let testVar1 = 'A';
        let testVar2 = 22;
        let testVar3 = {};
        let testVar4 = 'test4';

        beforeEach(() => {
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

        test('получает значения', () => {
            expect(getData('testA')).toEqual(testVar1);
            expect(getData('testB.testB2')).toEqual(testVar2);
            expect(getData('testC.testC2.testC3')).toEqual(testVar3);
            expect(getData('testC.testC2.testC3.wrongParam')).toBeUndefined();
        });

        test('получает значения c дефолтами', () => {
            expect(getData('testA', 'test1')).toEqual(testVar1);
            expect(getData('testB.testB2', 'test2')).toEqual(testVar2);
            expect(getData('testC.testC2.testC3', 'test3')).toEqual(testVar3);
            expect(getData('testC.testC2.testC3.wrongParam', testVar4)).toEqual(testVar4);
        });
    });
});
