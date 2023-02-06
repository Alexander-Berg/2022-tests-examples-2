import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';
import {throwError} from 'redux-saga-test-plan/providers';

import ErrorModalService from '_pkg/sagas/services/ErrorModalService';

import {entityDestroyer} from '../../entityLoader';
import {errorHandler} from '../../utils';
import {apiInstance, DATA} from './mocks/api';
import {pure} from './mocks/actions';

const actions = pure.testEntities;

const DESTROYER_OPTIONS = {
    actions
};

const originalLog = console.error;

describe('entityDestroyer', () => {
    beforeAll(() => {
        console.error = jest.fn(() => {});
    });

    afterAll(() => {
        console.error = originalLog;
    });

    test('Проверяем позитивный кейс удаления', () => {
        const destroyer = entityDestroyer(apiInstance, DESTROYER_OPTIONS);

        return expectSaga(destroyer, DATA[0])
            .put(actions.remove(DATA[0].id))
            .put(actions.removeSuccess(DATA[0].id))
            .run();
    });

    test('Проверяем негативный кейс удаления', () => {
        const error = new Error('Exception');
        const destroyer = entityDestroyer(apiInstance, DESTROYER_OPTIONS);

        // приходится экранировать ошибку через errorHandler
        // иначе не получится получить вызовы из результата
        return expectSaga(errorHandler(destroyer), DATA[0])
            .provide([
                [matchers.call.fn(apiInstance.remove), throwError(error)]
            ])
            .put(actions.remove(DATA[0].id))
            .put(actions.removeError(error))
            .run();
    });

    test('Проверяем что ошибки всплывают', () => {
        const error = new Error('Exception');
        const destroyer = entityDestroyer(apiInstance, DESTROYER_OPTIONS);
        const onErrorHandled = () => Promise.reject(new Error('Exceptions do not bubble'));
        const onErrorBubble = () => Promise.resolve();

        return expectSaga(destroyer, DATA[0])
            .provide([
                [matchers.call.fn(apiInstance.remove), throwError(error)]
            ])
            .run()
            .then(onErrorHandled, onErrorBubble);
    });

    test('Проверяем вызов модалки при ошибке', () => {
        const error = new Error('Exception');
        const destroyer = entityDestroyer(apiInstance, DESTROYER_OPTIONS);
        const saga = function * () {
            try {
                yield destroyer(DATA[0]);
            } catch (error) {
                // изолируем финальную ошибку, чтобы получить результат теста
            }
        };

        return expectSaga(saga)
            .provide([
                [matchers.call.fn(apiInstance.remove), throwError(error)]
            ])
            .call(ErrorModalService.add, error)
            .run();
    });

    test('Проверяем что ключ определятся через idKey', () => {
        const updater = entityDestroyer(apiInstance, {
            ...DESTROYER_OPTIONS,
            idKey: 'cid'
        });

        return expectSaga(updater, {...DATA[0], cid: 'client_id'})
            .put(actions.removeSuccess('client_id'))
            .run();
    });
});
