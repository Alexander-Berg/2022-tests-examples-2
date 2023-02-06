import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';

import {actions as modalActions} from '_pkg/reducers/modals';
import {confirm} from '_pkg/sagas/decorators';
import {GLOBAL_CONFIRM_MODAL_ID} from '_pkg/sagas/services/ConfirmModalService';

describe('confirmDecorator', () => {
    test('Декоратор бросает ошибку при отклонении диалога', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @confirm()
            public static method() {
                return 1;
            }
        }

        return expectSaga(function * () {
            try {
                return yield matchers.call(TestService.method);
            } catch (e) {
                return e;
            }
        })
            .dispatch(modalActions.close(GLOBAL_CONFIRM_MODAL_ID))
            .run()
            .then(runResult => {
                expect(runResult.returnValue instanceof Error).toBe(true);
            });
    });

    test('Декоратор вызывает метод после подтверждения и пробрасывает return', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @confirm()
            public static method(x?: number) {
                return x;
            }
        }

        return expectSaga(function * () {
            return yield matchers.call(TestService.method, 1);
        })
            .dispatch(modalActions.close(GLOBAL_CONFIRM_MODAL_ID, {}))
            .run()
            .then(runResult => {
                expect(runResult.returnValue).toBe(1);
            });
    });

    test('Декоратор принимает функцию', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @confirm(() => ({
                title: 'xxx'
            }))
            public static method() {
                return 1;
            }
        }

        return expectSaga(function * () {
            return yield matchers.call(TestService.method);
        })
            .dispatch(modalActions.close(GLOBAL_CONFIRM_MODAL_ID, 1))
            .run()
            .then(result => {
                const openAction = result.effects.put[0].payload.action;
                expect(openAction.payload.meta.title).toBe('xxx');
            });
    });
});
