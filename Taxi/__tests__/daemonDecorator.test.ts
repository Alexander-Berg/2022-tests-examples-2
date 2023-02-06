import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';

import {daemon, operation} from '_pkg/sagas/decorators';
import {DaemonMode} from '_pkg/sagas/utils';
import {Service} from '_types/common/infrastructure';

const TEST_ID = 'TEST_ID';

describe('daemonDecorator', () => {
    test('Создает операцию по умолчанию', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestServiceClass {
            public static toString = () => 'TestService';

            @daemon()
            public static method(): null {
                return null;
            }
        }
        const TestService = TestServiceClass as Service<typeof TestServiceClass>;

        expect(TestService.method).toHaveProperty('id');
        expect(TestService.method.id).toEqual('TEST_SERVICE_METHOD');
    });

    test('Использует существующую операцию, если есть', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestServiceClass {
            @daemon()
            @operation(TEST_ID)
            public static * method() {
                return 1;
            }
        }
        const TestService = TestServiceClass as Service<typeof TestServiceClass>;

        expect(TestService.method.id).toEqual(TEST_ID);
    });

    test('По умолчанию DaemonMode.Sync', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestServiceClass {
            @daemon()
            public static method(): null {
                return null;
            }
        }
        const TestService = TestServiceClass as Service<typeof TestServiceClass>;

        expect((TestService.method as any).__$daemonMode).toEqual(DaemonMode.Sync);
    });

    test('Декоратор пробрасывает возвращаемое значение', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @daemon()
            public static method() {
                return 1;
            }
        }

        return expectSaga(function * () {
            return yield matchers.call(TestService.method);
        })
            .run()
            .then(runResult => {
                expect(runResult.returnValue).toBe(1);
            });
    });
});
