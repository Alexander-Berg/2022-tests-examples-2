/* eslint-disable @typescript-eslint/no-explicit-any,@typescript-eslint/restrict-plus-operands */

import { logError } from '@lib/log/logError';
import { getView, ViewLevel, ExecView3Arg } from '../views';

jest.mock('../../log/logError.ts', () => {
    return {
        logError: jest.fn().mockImplementation(() => {
            throw new Error('logError called!');
        })
    };
});
const mockedLogError = logError as jest.Mock;

describe('home.views', function() {
    let testViews: ViewLevel;
    let execTestView: ExecView3Arg;

    beforeEach(() => {
        testViews = getView();
        execTestView = testViews.execView;
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    test('игнорирует дубликаты', function() {
        mockedLogError.mockImplementation(() => {});

        testViews('test-duplicate', () => 'first definition');
        testViews('test-duplicate', () => 'second definition');

        expect(execTestView('test-duplicate', {})).toEqual('first definition');

        expect(mockedLogError.mock.calls).toMatchSnapshot();
    });

    describe('наследование', function() {
        let view = getView();
        let execView = view.execView;
        let view2 = view.inherit();
        let execView2 = view2.execView;

        view('test-dev', () => 'test definition');

        view2('testSideEffect', () => 'ok');
        view2('ok', () => ': ok');

        test('использует базовые шаблоны', function() {
            expect(execView2('test-dev', {})).toEqual('test definition');
        });

        test('не влияет на базовые шаблоны', function() {
            expect(execView('testSideEffect', {})).toEqual('');

            view2('test-dev', () => 'test definition overloaded');

            expect(execView('test-dev', {})).toEqual('test definition');
        });

        test('добавляет шаблон', function() {
            expect(execView2('testSideEffect', {})).toEqual('ok');

            expect(execView2('test-dev', {})).toEqual('test definition overloaded');
        });

        let data = {
            key0: 'value0',
            key1: 'value1'
        };
        interface Data {
            key0: string;
            key1: string;
        }
        view('template', (data: Data) => data.key0);

        view('view-t0', (data: Data, req: Req3Server, execView: ExecViewCompat) => execView('view2-t1', data));

        view('view-t1', (data: Data, req: Req3Server, execView: ExecViewCompat) => execView('view2-t2', data));

        view('view-a0', (data: Data, req: Req3Server, execView: ExecViewCompat) => execView('view2-a0', data));

        view2('template2', (data: Data) => data.key1);

        view2('template3', (data: Data) => data.key1);

        view2('view2-t0', (data: Data, req: Req3Server, execView: ExecViewCompat) => execView('view-t0', data));

        view2('view2-t1', (data: Data, req: Req3Server, execView: ExecViewCompat) => execView('view-t1', data));

        view2('view2-t2', () => 'test');

        view2('view2-a0', (data: Data) => data.key1);

        test('подставляет данные в шаблон', function() {
            expect(execView('template', data)).toEqual('value0');

            expect(execView2('template2', data)).toEqual('value1');

            expect(execView2('template3', data)).toEqual('value1');
        });

        test('позволяет вызывать шаблоны из всех уровней', function() {
            expect(execView2('view2-t0', data)).toEqual('test');

            expect(execView2('view-a0', data)).toEqual('value1');
        });
    });

    test('поддерживает шаблоны без результата', function() {
        let views = getView();
        let total = 0;

        views('test', function() {
            ++total;
        });

        expect(views.execView('test', {})).toEqual('');
        expect(total).toEqual(1);
    });

    test('выполняет связанные шаблоны', function() {
        let views = getView();

        views('test', (data: UnusedData, req: Req3Server, exec: ExecViewCompat) => `abc ${exec('test2')}`);

        views('test2', () => '123');

        expect(views.execView('test', {})).toEqual('abc 123');
    });

    describe('req объект', function() {
        let view = getView();
        let execView = view.execView;

        interface Data {
            first?: string;
            second?: string;
        }

        view('req-seeker-str', (data: Data, req: Req3Server, exec: ExecViewCompat) => `${exec('req-seeker-func', data)} ${String(data.first)} ${String(data.second)}`);

        view('req-seeker-func', function(data: Data, req: Req3Server) {
            return data.first + ' and ' + req.first + req.second;
        });

        view('func-template', function(data: UnusedData, req: Req3Server, execView: ExecViewCompat) {
            return execView('req-seeker-func', {
                first: 'baz'
            });
        });

        view('func-override', function(data: UnusedData, req: Req3Server, execView: ExecView3Arg) {
            return execView.withReq('req-seeker-str', data, {
                first: 'override'
            } as unknown as Req3Server);
        });

        test('не теряется при вызове', function() {
            expect(execView('func-template', {
                first: 'foo',
                second: 'bar'
            })).toEqual('baz and foobar');
        });

        test('переопределяется при первом вызове', function() {
            expect(execView('req-seeker-str', {
                first: 'foo',
                second: 'bar'
            }, {
                first: 'baz',
                second: 'qwe'
            } as unknown as Req3Server)).toEqual('foo and bazqwe foo bar');
        });

        test('переопределяется при вызове execView', function() {
            expect(execView('func-override', {
                first: 'foo',
                second: 'bar'
            })).toEqual('foo and overrideundefined foo bar');
        });
    });

    describe('cached views', function() {
        let views = getView();

        views('sequence', (data: UnusedData, req: Req3Server, exec: ExecViewCompat) => `${exec('aaa')},${exec('aaa')},${exec('aaa')}`);

        interface Data {
            q?: string;
        }

        views('aaa', function(data: Data, req: Req3Server) {
            return 'parent' + ((req.a as string) + data.q) + '>';
        });

        test('не допускает использование строковых шаблонов', function() {
            let child = views.inherit();

            expect(function() {
                child.cached('aaa', 'bla [% req:HomePageNoArgs %]');
            }).toThrow(TypeError);
        });

        test('изолирует разные сессии', function() {
            let child = views.inherit();
            let cachedView = child.cached;
            let execView = child.execView;
            let times = 0;

            cachedView('aaa', function(req: Req3Server) {
                times++;
                return 'a!' + req.a;
            });

            expect(execView('aaa', { a: 42 })).toEqual('a!42');
            expect(times).toEqual(1);

            expect(execView('aaa', { a: 11 })).toEqual('a!11');
            expect(times).toEqual(2);
        });

        test('кэширует результат', function() {
            let child = views.inherit();
            let cachedView = child.cached;
            let execView = child.execView;
            let times = 0;

            cachedView('aaa', function(req: Req3Server) {
                times++;
                return 'a!' + req.a;
            });

            expect(execView('sequence', { a: 42 })).toEqual('a!42,a!42,a!42');
            expect(times).toEqual(1);
        });

        test('вызывает base', function() {
            let middle = views.inherit();
            let child = middle.inherit();
            let execView = child.execView;

            middle.cached('aaa', function aaa(req: Req3Server, execView: ExecViewCompat) {
                return execView((aaa as any).base, { q: 4 }) + '<middle' + ((req.a as number) - 1);
            });

            child.cached('aaa', function aaa(req: Req3Server, execView: ExecViewCompat) {
                return execView((aaa as any).base) + 'a!' + req.a;
            });
            expect(execView('aaa', { a: 12 })).toEqual('parent16><middle11a!12');
        });
    });

    describe('base', function() {
        let views = getView();
        let middle = views.inherit();
        let child = middle.inherit();
        let execView = child.execView;

        interface Data {
            a: unknown;
            q: unknown;
            w: unknown;
            e: unknown;
        }

        beforeAll(function() {
            middle('bbb', function() {
                return 'should not be called';
            });

            middle('aaa', function aaa(data: Data, req: Req3Server, execView: ExecViewCompat) {
                return 'middle:' + [data.a, req.q, execView('bbb', { a: 2 })];
            });

            child('aaa', function aaa(data: Data, req: Req3Server, execView: ExecViewCompat) {
                return 'child:' + [data.a, req.e] + execView((aaa as any).base, { a: 1 });
            });

            child('bbb', function(data: Data, req: Req3Server) {
                return 'child bbb:' + [data.a, req.w];
            });
        });

        test('допускает вызов из base шаблонов верхнего уровня', function() {
            expect(execView('aaa', {
                a: 0,
                q: 'middle req.q;',
                w: 'child req.w;',
                e: 'child req.e;'
            })).toEqual('child:0,child req.e;middle:1,middle req.q;,child bbb:2,child req.w;');
        });
    });

    test('Удаляет шаблоны из списка', function() {
        testViews('some', () => 'first definition');

        expect(execTestView('some', {})).toEqual('first definition');
        testViews.cleanViews(['some']);
        expect(execTestView('some', {})).toEqual('');

        testViews('some', () => 'second definition');

        expect(execTestView('some', {})).toEqual('second definition');
    });
});
