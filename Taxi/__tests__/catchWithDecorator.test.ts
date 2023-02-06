import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';

import {catchWith, NotificationMode} from '_pkg/sagas/decorators';
import NotificationService from '_pkg/sagas/services/NotificationService';

import pipe, {Invoke} from '../pipeDecorator';

describe('catchWithDecorator', () => {
    test('Декоратор отлавливает ошибку', () => {
        const errorHandler = jest.fn();

        // tslint:disable-next-line: max-classes-per-file
        class ErrorService {
            @pipe(function * () {
                return 1;
            }, Invoke.After)
            @catchWith(function * (error: Error, x: number) {
                yield matchers.call(errorHandler, x);
            })
            public static method(x: number) {
                throw new Error();
            }
        }

        return expectSaga(function * () {
            return yield matchers.call(ErrorService.method);
        })
            .run()
            .then(runResult => {
                expect(errorHandler).toHaveBeenCalled();
                expect(runResult.returnValue).toBe(1);
            });
    });

    test('Декоратор пробрасывает возвращаемое значение', () => {
        // tslint:disable-next-line: max-classes-per-file
        class ErrorService {

            @catchWith()
            public static method() {
                return 2;
            }
        }
        return expectSaga(function * () {
            return yield matchers.call(ErrorService.method);
        })
            .run()
            .then(runResult => {
                expect(runResult.returnValue).toBe(2);
            });
    });

    test('Декоратор пробрасывает аргументы в обработчик ошибки', () => {
        const errorHandler = jest.fn();

        // tslint:disable-next-line: max-classes-per-file
        class ErrorService {
            @pipe(function * () {
                return 1;
            }, Invoke.After)
            @catchWith(function * (error: Error, x: number) {
                yield matchers.call(errorHandler, x);
            })
            public static method(x: number) {
                throw new Error();
            }
        }

        return expectSaga(function * () {
            return yield matchers.call(ErrorService.method, 1);
        })
            .run()
            .then(runResult => {
                expect(errorHandler).toHaveBeenLastCalledWith(1);
            });
    });

    test('Есть дефолтный обработчик с нотификацией', () => {
        // tslint:disable-next-line: max-classes-per-file
        class ErrorService {

            @catchWith()
            public static method() {
                throw new Error();
            }
        }
        return expectSaga(function * () {
            return yield matchers.call(ErrorService.method);
        })
            .run()
            .then(runResult => {
                const notificationCall = runResult.effects.call.find(
                    c => c.payload.fn === NotificationService.add
                );

                expect(notificationCall).toBeTruthy();
                expect(notificationCall?.payload.args[0].mode).toBe(NotificationMode.Error);
            });
    });

    test('Декоратор сохраняет this', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @catchWith()
            public static method() {
                expect(this).toStrictEqual(TestService);
                return 1;
            }
        }

        return expectSaga(function * () {
            return yield matchers.call([TestService, TestService.method]);
        })
            .run()
            .then(runResult => {
                expect(runResult.returnValue).toEqual(1);
            });
    });
});
