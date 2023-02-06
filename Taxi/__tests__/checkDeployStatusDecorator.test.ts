import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';

import {mockRequest} from '_pkg/isomorphic/utils/mockRequest';
import {actions as modalActions} from '_pkg/reducers/modals';
import {checkDeployStatus} from '_pkg/sagas/decorators';
import {GLOBAL_CONFIRM_MODAL_ID} from '_pkg/sagas/services/ConfirmModalService';

window.XMLHttpRequest = mockRequest;
const TEST_URL = '/internal/api/lenta';

describe('checkDeployStatusDecorator', () => {
    describe('Выкатки запрещены', () => {
        beforeEach(() => {
            mockRequest.clear();
            mockRequest.addMock('get', TEST_URL).addResponse({can_deploy: false}, 200);
        });

        test('Декоратор бросает ошибку при отклонении диалога', () => {
            // tslint:disable-next-line: max-classes-per-file
            class TestService {
                @checkDeployStatus()
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
                @checkDeployStatus()
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
    });

    describe('Выкатки разрешены', () => {
        beforeEach(() => {
            mockRequest.clear();
            mockRequest.addMock('get', TEST_URL).addResponse({can_deploy: true}, 200);
        });

        test('Декоратор вызывает метод и пробрасывает return', () => {
            // tslint:disable-next-line: max-classes-per-file
            class TestService {
                @checkDeployStatus()
                public static method(x?: number) {
                    return x;
                }
            }

            return expectSaga(function * () {
                return yield matchers.call(TestService.method, 1);
            })
                .run()
                .then(runResult => {
                    expect(runResult.returnValue).toBe(1);
                });
        });
    });
});
