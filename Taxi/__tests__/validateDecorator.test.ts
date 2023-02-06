import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';

import {actions as formActions} from '_pkg/deprecated/rrf';
import {actions as modalErrorActions, constants} from '_pkg/reducers/modalError';
import {validate} from '_pkg/sagas/decorators';
import ErrorModalService from '_pkg/sagas/services/ErrorModalService';
import NotificationService from '_pkg/sagas/services/NotificationService';
import ValidationError from '_pkg/utils/errors/ValidationError';

import {ValidationAssertMode} from '../validateDecorator';

describe('validateDecorator', () => {
    test('Бросает ошибку валидации', () => {
        const validator = Object.assign(
            function* () {
                return false;
            },
            {model: 'modelA'}
        );

        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @validate(validator)
            public static method() {
                return 1;
            }
        }

        return expectSaga(function* () {
            try {
                return yield matchers.call(TestService.method);
            } catch (e) {
                return e;
            }
        })
            .run()
            .then(runResult => {
                expect(runResult.returnValue instanceof ValidationError).toBe(true);
            });
    });

    test('Декоратор пробрасывает возвращаемое значение', () => {
        const validator = Object.assign(
            function* () {
                return true;
            },
            {model: 'modelA'}
        );

        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @validate(validator)
            public static method() {
                return 1;
            }
        }

        return expectSaga(function* () {
            return yield matchers.call(TestService.method);
        })
            .run()
            .then(runResult => {
                expect(runResult.returnValue).toBe(1);
            });
    });

    test('Декоратор пробрасывает аргументы в валидатор', () => {
        const validator = Object.assign(
            function* ({x}: {x: boolean}) {
                return x;
            },
            {model: 'modelA'}
        );

        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @validate(validator, {
                args: (x: boolean) => ({x})
            })
            public static method(x: boolean) {
                return 1;
            }
        }

        return expectSaga(function* () {
            return yield matchers.call(TestService.method, true);
        })
            .run()
            .then(runResult => {
                expect(runResult.returnValue).toBe(1);
            });
    });

    test('В форме проставляется isPristine', () => {
        const MODEL = 'modelA';
        const validator = Object.assign(
            function* () {
                return true;
            },
            {model: MODEL}
        );

        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @validate(validator)
            public static method(x: boolean) {
                return 1;
            }
        }

        return expectSaga(function* () {
            try {
                return yield matchers.call(TestService.method, true);
            } catch {
                //
            }
        })
            .run()
            .then(runResult => {
                const actualAction = runResult.effects.put[0].payload.action;
                const expectedAction = formActions.setPristine(MODEL);

                expect(actualAction.type).toEqual(expectedAction.type);
            });
    });

    test('В форме не проставляется isPristine при resetPristine false', () => {
        const MODEL = 'modelA';
        const validator = Object.assign(
            function* () {
                return true;
            },
            {model: MODEL}
        );

        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @validate(validator, {resetPristine: false})
            public static method(x: boolean) {
                return 1;
            }
        }

        return expectSaga(function* () {
            try {
                return yield matchers.call(TestService.method, true);
            } catch {
                //
            }
        })
            .run()
            .then(runResult => {
                expect(runResult.effects.put).not.toBeDefined();
            });
    });

    test('Работает, если валидатор возвращает объект', () => {
        const validator = Object.assign(
            function* () {
                return {
                    isValid: false
                };
            },
            {model: 'modelA'}
        );

        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @validate(validator)
            public static method() {
                return 1;
            }
        }

        return expectSaga(function* () {
            try {
                return yield matchers.call(TestService.method, true);
            } catch (e) {
                return e;
            }
        })
            .run()
            .then(runResult => {
                expect(runResult.returnValue instanceof ValidationError).toBe(true);
            });
    });

    test('ValidationAssertMode.Modal показывает модалку', () => {
        const validator = Object.assign(
            function* () {
                return false;
            },
            {model: 'modelA'}
        );

        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @validate(validator, {
                assertMode: ValidationAssertMode.Modal
            })
            public static method() {
                return 1;
            }
        }

        const spy = jest.spyOn(ErrorModalService, 'add');

        return expectSaga(function* () {
            try {
                return yield matchers.call(TestService.method, true);
            } catch {
                //
            }
        })
            .run()
            .then(() => {
                expect(ErrorModalService.add).toHaveBeenCalled();
                spy.mockRestore();
            });
    });

    test('ValidationAssertMode.Notification показывает нотифайку', () => {
        const validator = Object.assign(
            function* () {
                return false;
            },
            {model: 'modelA'}
        );

        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @validate(validator, {
                assertMode: ValidationAssertMode.Notification
            })
            public static method() {
                return 1;
            }
        }

        const spy = jest.spyOn(NotificationService, 'error');

        return expectSaga(function* () {
            try {
                return yield matchers.call(TestService.method, true);
            } catch {
                //
            }
        })
            .run()
            .then(() => {
                expect(NotificationService.error).toHaveBeenCalled();
                spy.mockRestore();
            });
    });

    test('Принимает опцию валидатора showAssert в виде функции, возвращающей ошибку', () => {
        const ERROR_MESSAGE = 'ERROR_MESSAGE';
        const validator = Object.assign(
            function* () {
                return false;
            },
            {model: 'modelA', showAssert: () => ERROR_MESSAGE}
        );

        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @validate(validator, {
                assertMode: ValidationAssertMode.Modal
            })
            public static method(x: boolean) {
                return 1;
            }
        }

        return expectSaga(function* () {
            try {
                return yield matchers.call(TestService.method, true);
            } catch {
                //
            }
        })
            .run()
            .then(runResult => {
                const put = runResult.effects.put.find(p => p.payload.action.type === constants.ADD);
                expect(put).toBeTruthy();

                const actualAction = put!.payload.action;
                const expectedAction = modalErrorActions.add(ERROR_MESSAGE);

                expect(actualAction.type).toEqual(expectedAction.type);
                expect(actualAction.payload).toEqual(expectedAction.payload);
            });
    });
});
