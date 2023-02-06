import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';

import NotificationService from '_pkg/sagas/services/NotificationService';

import notify, {BaseNotification, NotificationMode} from '../notifyDecorator';

class CustomNotification extends BaseNotification<string> {}

// tslint:disable-next-line: max-classes-per-file
class TestService {
    @notify(CustomNotification)
    public static method() {
        return 1;
    }

    @notify((data: string) => {
        return new CustomNotification({mode: NotificationMode.Error, data});
    })
    public static method2(data: string) {
        return data;
    }

    @notify(BaseNotification)
    public static method3() {
        return 1;
    }
}

describe('notifyDecorator', () => {
    test('Декоратор добавляет нотификацию через конструктор', () => {
        return expectSaga(function * () {
            yield matchers.call(TestService.method);
            yield matchers.call(TestService.method);
        })
            .run()
            .then(runResult => {
                const notificationCall = runResult.effects.call.filter(
                    c => c.payload.fn === NotificationService.add
                );

                expect(notificationCall.length).toBe(2);

                const notification1: CustomNotification = notificationCall[0].payload.args[0];
                const notification2: CustomNotification = notificationCall[1].payload.args[0];

                expect(notification1 instanceof CustomNotification).toBe(true);
                expect(notification1.id).not.toBe(notification2.id);
                expect(notification1.mode).toBe(NotificationMode.Success);
            });
    });

    test('Декоратор добавляет нотификацию через фабрику', () => {
        return expectSaga(function * () {
            yield matchers.call(TestService.method2, '1');
            yield matchers.call(TestService.method2, '2');
        })
            .run()
            .then(runResult => {
                const notificationCall = runResult.effects.call.filter(
                    c => c.payload.fn === NotificationService.add
                );

                expect(notificationCall.length).toBe(2);

                const notification1: CustomNotification = notificationCall[0].payload.args[0];
                const notification2: CustomNotification = notificationCall[1].payload.args[0];

                expect(notification1 instanceof CustomNotification).toBe(true);
                expect(notification1.id).not.toBe(notification2.id);
                expect(notification1.mode).toBe(NotificationMode.Error);
                expect(notification2.data).toBe('2');
            });
    });

    test('Декоратор добавляет нотификацию через базовый конструктор', () => {
        return expectSaga(function * () {
            yield matchers.call(TestService.method3);
            yield matchers.call(TestService.method3);
        })
            .run()
            .then(runResult => {
                const notificationCall = runResult.effects.call.filter(
                    c => c.payload.fn === NotificationService.add
                );

                expect(notificationCall.length).toBe(2);

                const notification1: BaseNotification = notificationCall[0].payload.args[0];
                const notification2: BaseNotification = notificationCall[1].payload.args[0];

                expect(notification1 instanceof BaseNotification).toBe(true);
                expect(notification1.id).not.toBe(notification2.id);
                expect(notification1.mode).toBe(NotificationMode.Success);
            });
    });
});
