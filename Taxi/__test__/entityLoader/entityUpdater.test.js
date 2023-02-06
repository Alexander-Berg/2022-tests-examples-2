import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';
import {throwError} from 'redux-saga-test-plan/providers';

import ErrorModalService from '_pkg/sagas/services/ErrorModalService';

import {entityUpdater} from '../../entityLoader';
import {errorHandler} from '../../utils';
import {apiInstance, DATA} from './mocks/api';
import {pure} from './mocks/actions';

const actions = pure.testEntities;

const originalLog = console.error;

const UPDATER_OPTIONS = {
    actions: {
        ...actions,
        updateSuccess: result =>
            actions.updateSuccess(result.id, result)
    }
};

describe('entityUpdater', () => {
    beforeAll(() => {
        console.error = jest.fn(() => {});
    });

    afterAll(() => {
        console.error = originalLog;
    });

    test('Проверяем позитивный кейс апдейта', () => {
        const updater = entityUpdater(apiInstance, UPDATER_OPTIONS);

        return expectSaga(updater, DATA[0])
            .put(actions.update(DATA[0].id))
            .put(actions.updateSuccess(DATA[0].id, {...DATA[0], val: DATA[0].val + 1}))
            .run();
    });

    test('Проверяем негативный кейс апдейта', () => {
        const error = new Error('Exception');
        const updater = entityUpdater(apiInstance, UPDATER_OPTIONS);

        // приходится экранировать ошибку через errorHandler
        // иначе не получится получить вызовы из результата
        return expectSaga(errorHandler(updater), DATA[0])
            .provide([
                [matchers.call.fn(apiInstance.update), throwError(error)]
            ])
            .put(actions.update(DATA[0].id))
            .put(actions.updateError(error))
            .run();
    });

    test('Проверяем что ошибки всплывают', () => {
        const error = new Error('Exception');
        const updater = entityUpdater(apiInstance, UPDATER_OPTIONS);
        const onErrorHandled = () => Promise.reject(new Error('Exceptions do not bubble'));
        const onErrorBubble = () => Promise.resolve();

        return expectSaga(updater, DATA[0])
            .provide([
                [matchers.call.fn(apiInstance.update), throwError(error)]
            ])
            .run()
            .then(onErrorHandled, onErrorBubble);
    });

    test('Проверяем что результат mergeData попадает в АПИ', () => {
        const updater = entityUpdater(apiInstance, {
            ...UPDATER_OPTIONS,
            mergeData: (data, state) => ({...data, ...state})
        });
        const initialState = {info: 'info'};
        const reducer = (state = initialState, action) => state;

        return expectSaga(updater, DATA[0])
            .withReducer(reducer)
            .run()
            .then(result => {
                const {call} = result.effects;
                const apiCall = call.find(e => e.payload.fn === apiInstance.update);
                expect(apiCall.payload.args[0]).toEqual({...DATA[0], ...initialState});
            });
    });

    test('Проверяем что результат mergeResponse попадает в редьюссер', () => {
        const updater = entityUpdater(apiInstance, {
            ...UPDATER_OPTIONS,
            mergeResponse: (response, data) => ({...data, ...response, resp: 'resp'})
        });
        const data = {...DATA[0], val: DATA[0].val + 1, resp: 'resp'};

        return expectSaga(updater, DATA[0])
            .put(actions.updateSuccess(DATA[0].id, data))
            .run();
    });

    test('Проверяем что ключ определятся через idKey', () => {
        const updater = entityUpdater(apiInstance, {
            ...UPDATER_OPTIONS,
            idKey: 'noSuchProperty'
        });

        return expectSaga(updater, DATA[0])
            .run()
            .then(result => {
                const {put} = result.effects;
                const successPut = put.find(e => e.payload.action.type === actions.createSuccess().type);

                // поскольку мы в качестве ключа указали несуществующее свойство,
                // айдишник не нашелся и произошел create
                expect(successPut).toBeTruthy();
            });
    });

    test('Проверяем вызов модалки при ошибке', () => {
        const error = new Error('Exception');
        const updater = entityUpdater(apiInstance, UPDATER_OPTIONS);
        const saga = function * () {
            try {
                yield updater(DATA[0]);
            } catch (error) {
                // изолируем финальную ошибку, чтобы получить результат теста
            }
        };

        return expectSaga(saga)
            .provide([
                [matchers.call.fn(apiInstance.update), throwError(error)]
            ])
            .call(ErrorModalService.add, error)
            .run();
    });
});
