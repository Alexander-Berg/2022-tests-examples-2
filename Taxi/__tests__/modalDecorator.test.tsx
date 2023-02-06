
import {mount} from 'enzyme';
import React, {useEffect} from 'react';
import {Provider} from 'react-redux';
import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';
import {call, put} from 'redux-saga/effects';

// tslint:disable: cross-layers-imports
import modalConfirm, {getCustomModelFormName} from '_pkg/components/hocs/modal-confirm';
import modalManager from '_pkg/components/hocs/modal-manager';
import store, {sagaMiddleware} from '_pkg/infrastructure/store';
import {hasReducer} from '_pkg/reducers/';
import reducer, {actions as modalsActions} from '_pkg/reducers/modals';
import {modal} from '_pkg/sagas/decorators';
import {service as fnService} from '_pkg/sagas/services/FnComponentLoadService';
import {createService} from '_pkg/sagas/utils';
import {createDeferred, Deferred} from '_pkg/utils/createDeferred';

import daemon from '../daemonDecorator';

const MODAL_ID = 'FAKE_MODAL_ID';
const CUSTOM_MODEL = 'CUSTOM_MODEL';

describe('modalDecorator', () => {
    test('Указываем кастомную модель для модалки', () => {
        const mockFn = jest.fn();
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @daemon()
            @modal(MODAL_ID)
            public static * method(...args: [number, Indexed?]) {
                mockFn(...args);
            }
        }

        const service = createService(TestService);
        let renderDeferred: Deferred<void> = createDeferred();

        const Root = modalManager(({children}) => {
            useEffect(() => {
                renderDeferred.resolve();

                return () => {
                    renderDeferred = createDeferred();
                };
            });

            return <div>{children}</div>;
        });

        const Modal = modalConfirm({modalId: MODAL_ID, modalModel: CUSTOM_MODEL})(({submit}) => (
            <div id="modal">
                <button onClick={submit}/>
            </div>
        ));

        return sagaMiddleware.run(function * () {
            yield call(fnService.run);
            yield call(service.run);

            const tree = mount(
                <Provider store={store}>
                    <Root>
                        <Modal/>
                    </Root>
                </Provider>
            );

            yield put(service.actions.method(1));
            yield renderDeferred.promise;
            tree.update();

            const modal = tree.find('#modal');
            const modalModel = modal.parent().prop('model');
            expect(modalModel).toEqual(CUSTOM_MODEL);
            expect(hasReducer(CUSTOM_MODEL)).toBeTruthy();
            expect(hasReducer(getCustomModelFormName(CUSTOM_MODEL))).toBeTruthy();
            yield call(service.destroy);
            yield call(fnService.destroy);
        })
            .toPromise();
    });

    test('Интеграционный тест', () => {
        const mockFn = jest.fn();
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @daemon()
            @modal(MODAL_ID)
            public static * method(...args: [number, Indexed?]) {
                mockFn(...args);
            }
        }

        const service = createService(TestService);
        let renderDeferred: Deferred<void> = createDeferred();

        const Root = modalManager(({children}) => {
            useEffect(() => {
                renderDeferred.resolve();

                return () => {
                    renderDeferred = createDeferred();
                };
            });

            return <div>{children}</div>;
        });

        const Modal = modalConfirm({modalId: MODAL_ID})(({submit}) => (
            <div id="modal">
                <button onClick={submit}/>
            </div>
        ));

        return sagaMiddleware.run(function * () {
            yield call(fnService.run);
            yield call(service.run);

            const tree = mount(
                <Provider store={store}>
                    <Root>
                        <Modal/>
                    </Root>
                </Provider>
            );

            expect(tree.find('#modal').length).toBe(0);
            yield put(service.actions.method(1));

            yield renderDeferred.promise;
            tree.update();

            const modal = tree.find('#modal');
            expect(modal.length).toBe(1);

            const modalProps = modal.parent().props();
            expect(modalProps).toHaveProperty('args', [1]);
            expect(modalProps).toHaveProperty('submit');
            expect(modalProps).toHaveProperty('operationId');
            expect(modalProps).toHaveProperty('submitOperationId');
            expect(modalProps).toHaveProperty('model');
            expect(modalProps).toHaveProperty('close');

            modal.find('button').props().onClick?.(null!);

            yield renderDeferred.promise;
            tree.update();

            expect(mockFn).toBeCalledWith(1, {}); // пустой объект - модель модалки
            expect(tree.find('#modal').length).toBe(0);

            yield call(service.destroy);
            yield call(fnService.destroy);
        })
            .toPromise();
    });

    test('Декоратор вызывает открытие модалки c аргументами', () => {
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @modal(MODAL_ID)
            public static method(x: number) {
                //
            }
        }

        return expectSaga(function * () {
            return yield matchers.call(TestService.method, 1);
        })
            .run()
            .then(result => {
                const {type, payload: {id, meta: {submit, ...meta}}} = result.effects.put[0].payload.action;
                expect(submit).toBeTruthy();
                expect({type, payload: {id, meta}}).toEqual(modalsActions.open(MODAL_ID, {args: [1]}));
            });
    });

    test('Метод срабатывает на сабмит и получает результат модалки', () => {
        const mockFn = jest.fn((x: number, modalData?: any) => ({}));
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @modal(MODAL_ID)
            public static method(x: number, modalData?: any) {
                mockFn(x, modalData);
            }
        }

        return expectSaga(function * (): Gen {
            yield matchers.fork(function * () {
                yield matchers.call(TestService.method, 1);
            });

            yield matchers.take(`${modalsActions.open}`);
            const {submit} = yield matchers.select((s: Indexed) => s[MODAL_ID]);
            yield matchers.call(submit, 2);
        })
            .withReducer(reducer)
            .run()
            .then(() => {
                expect(mockFn).toHaveBeenCalledTimes(1);
                expect(mockFn).toHaveBeenLastCalledWith(1, 2);
            });
    });

    test('После звршения метода закрывается модалка', () => {
        const mockFn = jest.fn(() => ({}));
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @modal(MODAL_ID)
            public static method(x: number) {
                mockFn();
            }
        }

        return expectSaga(function * (): Gen {
            yield matchers.fork(function * () {
                yield matchers.call(TestService.method, 1);
            });

            yield matchers.take(`${modalsActions.open}`);
            const {submit} = yield matchers.select((s: Indexed) => s[MODAL_ID]);
            yield matchers.call(submit);
        })
            .withReducer(reducer)
            .run()
            .then(result => {
                const {action} = result.effects.put[1].payload;
                expect(action).toEqual(modalsActions.close(MODAL_ID));
            });
    });

    test('Декоратор сохраняет this при прямом вызове', () => {
        const mockFn = jest.fn();

        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @modal(MODAL_ID)
            public static method() {
                expect(this).toEqual(TestService);
                mockFn();

                return 1;
            }
        }

        return expectSaga(function * (): Gen {
            yield matchers.fork(function * () {
                const res: number = yield matchers.call([TestService, TestService.method]);
                expect(res).toEqual(1);
            });

            yield matchers.take(`${modalsActions.open}`);
            const {submit} = yield matchers.select((s: Indexed) => s[MODAL_ID]);
            yield matchers.call(submit);
        })
            .withReducer(reducer)
            .run()
            .then(() => {
                expect(mockFn).toHaveBeenCalledTimes(1);
            });
    });
});
