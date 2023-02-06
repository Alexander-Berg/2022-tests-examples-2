import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';
import {delay} from 'redux-saga/effects';

import {pure as commonActions} from '_pkg/infrastructure/actions';
import NotificationService from '_pkg/sagas/services/NotificationService';
import i18n from '_pkg/utils/localization/i18n';

import {formSagaFactory, Modes} from '../form';
import {pure} from './entityLoader/mocks/actions';
import EntityCtr, {apiInstance} from './entityLoader/mocks/api';

const actions = pure.testEntities;

const OPTIONS = {
    actions,
    model: 'model'
};

const {load} = commonActions.form;

describe('formSagaFactory', () => {
    test('Имеет ожидаемую структуру', () => {
        const form = formSagaFactory(apiInstance, OPTIONS);

        expect(form.loadId).toBeTruthy();
        expect(form.saveId).toBeTruthy();
        expect(form.run).toBeTruthy();
        expect(form.destroy).toBeTruthy();
    });

    test('Запускается в режиме create', () => {
        const modelDefaults = {x: 1};
        const form = formSagaFactory(apiInstance, {...OPTIONS, modelDefaults});

        const saga = function * () {
            yield form.run({args: {mode: Modes.Create}});
            yield delay(0);
            yield form.destroy();
        };

        return expectSaga(saga)
            .put(load('model', modelDefaults))
            .run();
    });

    test('Можно определить modelDefaults через функцию', () => {
        const modelDefaults = () => ({x: 1});
        const form = formSagaFactory(apiInstance, {...OPTIONS, modelDefaults});

        const saga = function * () {
            yield form.run({args: {mode: Modes.Create}});
            yield delay(0);
            yield form.destroy();
        };

        return expectSaga(saga)
            .put(load('model', {x: 1}))
            .run();
    });

    test('Запускается в режиме edit', () => {
        const modelDefaults = {x: 1};
        const res = {y: 1};
        const id = '10';
        const form = formSagaFactory(apiInstance, {...OPTIONS, modelDefaults});

        const saga = function * () {
            yield form.run({args: {mode: Modes.Edit, id}});
            yield delay(0);
            yield form.destroy();
        };

        return expectSaga(saga)
            .provide([
                [matchers.call.fn(apiInstance.find), res]
            ])
            .put(actions.find(id))
            .put(actions.findSuccess(id, res))
            .put(load('model', {...modelDefaults, ...res}))
            .run();
    });

    test('Работает сохранение в режиме create', () => {
        const form = formSagaFactory(apiInstance, {...OPTIONS});
        const args = {mode: Modes.Create};

        const saga = function * () {
            yield form.run({args});
            yield delay(20);
            yield form.destroy();
        };

        const data = {z: 3};

        return expectSaga(saga)
            .withState({model: data})
            .dispatch(commonActions.formUI.save(EntityCtr))
            .call(apiInstance.create, data, args)
            .run();
    });

    test('Работает сохранение в режиме edit', () => {
        const form = formSagaFactory(apiInstance, {...OPTIONS});
        const args = {mode: Modes.Edit, id: '1'};

        const saga = function * () {
            yield form.run({args});
            yield delay(20);
            yield form.destroy();
        };

        const data = {z: 3};

        return expectSaga(saga)
            .withState({model: data})
            .dispatch(commonActions.formUI.save(EntityCtr))
            .call(apiInstance.update, data, args)
            .run();
    });

    test('Работает удаление', () => {
        const form = formSagaFactory(apiInstance, {...OPTIONS});

        const saga = function * () {
            yield form.run({args: {mode: Modes.Edit, id: '1'}});
            yield delay(20);
            yield form.destroy();
        };

        const data = {id: 1};

        return expectSaga(saga)
            .withState({model: data})
            .dispatch(commonActions.formUI.remove(EntityCtr, data))
            .call(apiInstance.remove, data)
            .run();
    });

    test('При сохранении показывается уведомление, если включить showSuccessNotify', () => {
        const form = formSagaFactory(apiInstance, {...OPTIONS, showSuccessNotify: true});
        const args = {mode: Modes.Edit, id: '1'};

        const saga = function * () {
            yield form.run({args});
            yield delay(20);
            yield form.destroy();
        };

        return expectSaga(saga)
            .withState({model: {}})
            .dispatch(commonActions.formUI.save(EntityCtr))
            .call(apiInstance.update, {}, args)
            .run()
            .then(runResult => {
                const notificationCall = runResult.effects.call.find(
                    c => c.payload.fn === NotificationService.success
                );

                expect(notificationCall).toBeTruthy();
            });
    });

    test('При удалении показывается уведомление, если включить showSuccessNotify', () => {
        const form = formSagaFactory(apiInstance, {...OPTIONS, showSuccessNotify: true});

        const saga = function * () {
            yield form.run({args: {mode: Modes.Edit, id: '1'}});
            yield delay(30);
            yield form.destroy();
        };

        return expectSaga(saga)
            .withState({model: {}})
            .dispatch(commonActions.formUI.remove(EntityCtr, {}))
            .call(apiInstance.remove, {})
            .run()
            .then(runResult => {
                const notificationCall = runResult.effects.call.find(
                    c => c.payload.fn === NotificationService.success
                );

                expect(notificationCall).toBeTruthy();
            });
    });

    test('Работает валидация', () => {
        const validate = () => false;
        const form = formSagaFactory(apiInstance, {...OPTIONS, validate});

        const saga = function * () {
            yield form.run({args: {mode: Modes.Edit, id: '1'}});
            yield delay(10);
            yield form.destroy();
        };

        return expectSaga(saga)
            .withState({model: {}})
            .dispatch(commonActions.formUI.save(EntityCtr))
            .put(commonActions.modalError.add(i18n.print('fill_out_all_data')))
            .not.call.fn(apiInstance.create)
            .run();
    });
});
