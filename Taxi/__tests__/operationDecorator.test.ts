import {expectSaga} from 'redux-saga-test-plan';
import {call} from 'typed-redux-saga';

import {confirm, notifySuccess, operation} from '_pkg/sagas/decorators';
import {AsyncOperation, OperationId, Service} from '_types/common/infrastructure';

const TEST_ID = 'TEST_ID';
const TEST_ID_TYPES = 'TEST_ID_TYPES' as OperationId<number>;

describe('operationDecorator', () => {
    test('Работает без аргументов', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestServiceClass {
            public static toString = () => 'TestService';

            @operation
            public static * operation() {
                return 1;
            }
        }
        const TestService = TestServiceClass as Service<typeof TestServiceClass>;

        expect(TestService.operation).toHaveProperty('id');
        expect(TestService.operation.id).toEqual('TEST_SERVICE_OPERATION');
    });

    test('Работает с id', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestServiceClass {
            public static toString = () => 'TestService';

            @operation(TEST_ID)
            public static * operation() {
                return 1;
            }

            // @ts-expect-error
            @operation(TEST_ID_TYPES)
            public static * operation2() {
                return '1';
            }

            @operation(TEST_ID_TYPES)
            public static * operation3() {
                return 1;
            }
        }
        const TestService = TestServiceClass as Service<typeof TestServiceClass>;

        expect(TestService.operation.id).toEqual(TEST_ID);
    });

    test('Работает с объектом', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestServiceClass {
            public static toString = () => 'TestService';

            // @ts-expect-error
            @operation({id: TEST_ID_TYPES})
            public static * operation() {
                return '1';
            }

            @operation({id: TEST_ID_TYPES})
            public static * operation2() {
                return 1;
            }
        }
        const TestService = TestServiceClass as Service<typeof TestServiceClass>;

        expect(TestService.operation.id).toEqual(TEST_ID_TYPES);
    });

    test('Допустима что внешняя опреация скрывает внутренние (ее id торчит наружу)', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestServiceClass {
            @operation(TEST_ID)
            @operation('xxx')
            public static * operation() {
                return 1;
            }
        }
        const TestService = TestServiceClass as Service<typeof TestServiceClass>;

        expect(TestService.operation.id).toEqual(TEST_ID);
    });

    test('Пробрасывает id даже если операция не является верхним декоратором', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestServiceClass {

            @notifySuccess()
            @confirm()
            @operation(TEST_ID)
            public static * operation() {
                return 1;
            }
        }
        const TestService = TestServiceClass as Service<typeof TestServiceClass>;

        expect(TestService.operation.id).toEqual(TEST_ID);
    });

    test('Декоратор пробрасывает возвращаемое значение', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @operation
            public static * method() {
                return 1;
            }
        }

        return expectSaga(function * () {
            return yield* call(TestService.method);
        })
            .run()
            .then(runResult => {
                expect(runResult.returnValue).toBe(1);
            });
    });

    test('Декоратор применяет стратегию обработки операций', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @operation({
                updateStrategy: function * ({result, ...rest}: AsyncOperation<number, [number]>) {
                    return {result: (result || 0) + 1, ...rest};
                }
            })
            public static * method(x: number) {
                return 1;
            }

            // @ts-expect-error
            @operation({
                updateStrategy: ({result, ...rest}: AsyncOperation<number>) => {
                    return {result: (result || 0) + 1, ...rest};
                }
            })
            public static * method2() {
                return '1';
            }

            // @ts-expect-error
            @operation({
                id: 'xxx' as OperationId<string>,
                updateStrategy: ({result, ...rest}: AsyncOperation<number>) => {
                    return {result: (result || 0) + 1, ...rest};
                }
            })
            public static * method3() {
                return 1;
            }

            // @ts-expect-error
            @operation({
                id: TEST_ID_TYPES,
                updateStrategy: ({result, ...rest}: AsyncOperation<number, [string]>) => {
                    return {result: (result || 0) + 1, ...rest};
                }
            })
            public static * method4(x: number) {
                return 1;
            }
        }

        return expectSaga(function * () {
            return yield* call(TestService.method, 0);
        })
            .run()
            .then(runResult => {
                const result = runResult.effects.put[1].payload.action.payload.result;
                expect(result).toBe(2);
            });
    });

    test('Декоратор сохраняет this', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @operation
            public static * method() {
                expect(this).toStrictEqual(TestService);
                return 1;
            }
        }

        return expectSaga(function * () {
            return yield* call([TestService, TestService.method]);
        })
            .run()
            .then(runResult => {
                expect(runResult.returnValue).toBe(1);
            });
    });

    test('Декоратор можно навешивать на приватные методы', () => {
        // @ts-ignore
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @operation({
                updateStrategy: function * ({result}: {result: number}) {
                    return {result};
                }
            })
            private static * method() {
                return 1;
            }

            public static method2() {
                return TestService.method();
            }
        }
    });

    test('Декоратор можно использовать с функцией', () => {
        // @ts-ignore
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @operation({
                id: (x: number) => x.toString() as OperationId<number, [number]>,
                updateStrategy: function * ({result}: AsyncOperation<number, [number]>) {
                    return {result};
                }
            })
            private static * method(x: number) {
                return x;
            }

            @operation({
                id: (x: number) => `${x}_2` as OperationId<number, [number]>
            })
            public static * method2(x: number) {
                return yield* call(TestService.method, x);
            }

            @operation((x: number) => `${x}_3` as OperationId<number, [number]>)
            public static * method3(x: number) {
                return yield* call(TestService.method2, x);
            }

            // @ts-expect-error
            @operation({
                id: (x: number) => x.toString() as OperationId<number, [number]>,
                updateStrategy: ({result}: AsyncOperation<number, [number]>) => ({result})
            })
            public static * method4(x: number) {
                return '1';
            }

            // @ts-expect-error
            @operation({
                id: (x: number) => `${x}_2` as OperationId<number, [number]>
            })
            public static * method5(x: string) {
                return x;
            }

            // @ts-expect-error
            @operation((x: number) => `${x}_3` as OperationId<number, [number]>)
            public static * method6() {
                return yield* call(TestService.method, 1);
            }

            @operation(() => '7' as OperationId<number>)
            public static * method7() {
                return yield* call(TestService.method, 1);
            }
        }
    });
});
