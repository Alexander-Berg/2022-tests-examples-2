import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';

import NotificationService from '_pkg/sagas/services/NotificationService';
import {NotificationMode} from '_pkg/utils/notifications/BaseNotification';

import notifySuccess from '../notifySuccessDecorator';

const SUCCESS_MESSAGE = 'SUCCESS_MESSAGE';

describe('notifySuccessDecorator', () => {
    test('Декоратор бросает нотификацию при успешном выполнении метода', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestService {

            @notifySuccess(SUCCESS_MESSAGE)
            public static method() {
                return 1;
            }
        }

        return expectSaga(function * () {
            return yield matchers.call(TestService.method);
        })
            .run()
            .then(runResult => {
                const notificationCall = runResult.effects.call.find(
                    c => c.payload.fn === NotificationService.add
                );

                expect(notificationCall).toBeTruthy();
                expect(notificationCall?.payload.args[0].mode).toBe(NotificationMode.Success);
                expect(notificationCall?.payload.args[0].data).toBe(SUCCESS_MESSAGE);
            });
    });

    test('В случае ошибки нотификации не будет', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @notifySuccess(SUCCESS_MESSAGE)
            public static method() {
                throw new Error();
            }
        }

        return expectSaga(function * () {
            try {
                return yield matchers.call(TestService.method);
            } catch (e) {
                return e;
            }
        })
            .run()
            .then(runResult => {
                expect(!runResult.effects.put).toBe(true);
                expect(runResult.returnValue instanceof Error).toBe(true);
            });
    });

    test('Декоратор пробрасывает возвращаемое значение', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @notifySuccess(SUCCESS_MESSAGE)
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
