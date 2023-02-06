import {expectSaga} from 'redux-saga-test-plan';
import {call, fork, put, select} from 'redux-saga-test-plan/matchers';

import {exact} from '_types/__test__/asserts';
import {OperationId, Service} from '_types/common/infrastructure';

import asyncOperations from '_pkg/reducers/asyncOperations';

import {daemon, operation} from '../decorators';
import {createService} from '../utils';

describe('createService', () => {
    test('сохраняет this', () => {
        const mockFn = jest.fn();

        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            public static toString = () => 'TestService';

            @daemon()
            public static *method() {
                expect(this).toEqual(TestService);
                mockFn();
            }
        }

        const service = createService(TestService);

        return expectSaga(function* () {
            yield fork(service.run);
            yield put(service.actions.method());
        })
            .silentRun(0)
            .then(() => {
                expect(mockFn).toHaveBeenCalledTimes(1);
            });
    });
    test('сохраняет this для унаследованных методов', () => {
        const mockFn = jest.fn();

        // tslint:disable-next-line: max-classes-per-file
        class TestServiceA {
            @daemon()
            public static *method(): Generator<unknown> {
                expect(this).toEqual(TestServiceB);
                mockFn();
            }
        }

        // tslint:disable-next-line: max-classes-per-file
        class TestServiceB extends TestServiceA {
            public static toString = () => 'TestServiceB';

            @daemon()
            public static *method() {
                expect(this).toEqual(TestServiceB);
                yield call([this, super.method]);
                mockFn();
            }
        }

        const service = createService(TestServiceB);

        return expectSaga(function* () {
            yield fork(service.run);
            yield put(service.actions.method());
        })
            .silentRun(0)
            .then(() => {
                expect(mockFn).toHaveBeenCalledTimes(2);
            });
    });

    test('Service Типизирует айдишники операций у методов', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            public static toString = () => 'TestService';

            public static *method(a: number, b?: string) {
                return 1;
            }
        }

        const Srv = TestService as Service<typeof TestService>;

        exact<typeof Srv.method.id, undefined | OperationId<number, [number, string?]>>(true);
        exact<typeof Srv.method.id, undefined | OperationId<{}, [number, string?]>>(false);
        exact<typeof Srv.method.id, undefined | OperationId<number, [number, string]>>(false);

        exact<typeof Srv.toString.id, undefined | string>(true);
    });

    test('Service корректно обрабатывает операции', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            public static toString = () => 'TestService';

            @operation
            public static *method() {
                return 1;
            }

            @operation((x: number) => `${x}` as OperationId<number>)
            public static *method2(x: number) {
                return 1;
            }

            @daemon()
            @operation((x: number) => `${x}` as OperationId<number>)
            public static *method3(x: number) {
                return 1;
            }
        }

        const Srv = TestService as Service<typeof TestService>;

        const service = createService(Srv);

        return expectSaga(function * () {
            yield call(service.run);
            yield call(TestService.method);
            yield call(TestService.method2, 10);
            yield call(TestService.method2, 11);
            yield call(TestService.method3, 12);
            yield call(TestService.method3, 13);

            let state = (yield select(s => s)) as any as Indexed;
            expect(state[Srv.method.id!]).toBeTruthy();
            expect(state['10']).toBeTruthy();
            expect(state['11']).toBeTruthy();
            expect(state['12']).toBeTruthy();
            expect(state['13']).toBeTruthy();

            yield call(service.destroy);

            state = (yield select()) as any as Indexed;
            expect(state[Srv.method.id!]).toBe(undefined);
            expect(state['10']).toBe(undefined);
            expect(state['11']).toBe(undefined);
            expect(state['12']).toBe(undefined);
            expect(state['13']).toBe(undefined);
        })
            .withReducer(asyncOperations)
            .run();
    });
});
