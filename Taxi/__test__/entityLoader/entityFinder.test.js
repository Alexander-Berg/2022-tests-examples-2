import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';
import {throwError} from 'redux-saga-test-plan/providers';

import ErrorModalService from '_pkg/sagas/services/ErrorModalService';

import {entityFinder} from '../../entityLoader';
import {errorHandler} from '../../utils';
import {apiInstance, DATA} from './mocks/api';
import {pure} from './mocks/actions';

const actions = pure.testEntities;

const FINDER_OPTIONS = {
    actions
};

const originalLog = console.error;

describe('entityFinder', () => {
    beforeAll(() => {
        console.error = jest.fn(() => {});
    });

    afterAll(() => {
        console.error = originalLog;
    });

    test('Проверяем позитивный кейс поиска', () => {
        const finder = entityFinder(apiInstance, FINDER_OPTIONS);

        return expectSaga(finder, DATA[0].id)
            .put(actions.find(DATA[0].id))
            .put(actions.findSuccess(DATA[0].id))
            .run();
    });

    test('Проверяем негативный кейс поиска', () => {
        const error = new Error('Exception');
        const finder = entityFinder(apiInstance, FINDER_OPTIONS);

        // приходится экранировать ошибку через errorHandler
        // иначе не получится получить вызовы из результата
        return expectSaga(errorHandler(finder), DATA[0].id)
            .provide([
                [matchers.call.fn(apiInstance.find), throwError(error)]
            ])
            .put(actions.find(DATA[0].id))
            .put(actions.findError(error))
            .run();
    });

    test('Проверяем что ошибки всплывают', () => {
        const error = new Error('Exception');
        const finder = entityFinder(apiInstance, FINDER_OPTIONS);
        const onErrorHandled = () => Promise.reject(new Error('Exceptions do not bubble'));
        const onErrorBubble = () => Promise.resolve();

        return expectSaga(finder, DATA[0].id)
            .provide([
                [matchers.call.fn(apiInstance.find), throwError(error)]
            ])
            .run()
            .then(onErrorHandled, onErrorBubble);
    });

    test('Проверяем вызов модалки при ошибке', () => {
        const error = new Error('Exception');
        const finder = entityFinder(apiInstance, FINDER_OPTIONS);
        const saga = function * () {
            try {
                yield finder(DATA[0].id);
            } catch (error) {
                // изолируем финальную ошибку, чтобы получить результат теста
            }
        };

        return expectSaga(saga)
            .provide([
                [matchers.call.fn(apiInstance.find), throwError(error)]
            ])
            .call(ErrorModalService.add, error)
            .run();
    });
});
