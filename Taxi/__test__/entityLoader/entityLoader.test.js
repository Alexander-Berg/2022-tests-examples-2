import {expectSaga} from 'redux-saga-test-plan';
import {delay} from 'redux-saga/effects';
import * as matchers from 'redux-saga-test-plan/matchers';

import {pure as commonActions} from '_pkg/infrastructure/actions';
import operationsReducer from '_pkg/reducers/asyncOperations';

import {entityLoader, ENTITY_LOADER_DEFAULTS} from '../../entityLoader';
import EntityCtr, {apiInstance, DATA, API_TIMEOUT} from './mocks/api';
import reducer from './mocks/reducer';
import {pure as actions} from './mocks/actions';

const originalLog = console.error;

const LODER_OPTIONS = {
    actions: {
        ...actions.testEntities,
        loadSuccess: result =>
            actions.testEntities.loadSuccess(result.items, result.meta),
        requestSuccess: result =>
            actions.testEntities.requestSuccess(result.items, result.meta)
    }
};

// используем для таймаутов в delay после запросов
//
// для опции timeout в run выставляем число запросов в тесте + 1, чтобы могла выполнится логика после последнего запроса
const requestsTime = requestsCount => ((API_TIMEOUT + 10) * requestsCount);

// При написании тестов нужно обязательно проверять,
// что при неправильной работе тест фейлится.
// В этих тестах лего получить ложно положительный результат
// при написании из-за неверных таймаутов например.
// Ложно отрицательный тоже можно получить из-за неверных таймаутов.
// (Речь про написание и отладку, а не про то что результвты в тестах рандомные)
//
// рекомендуется локально проверить при помощи разных значений API_TIMEOUT,
// что тесты проходят при эмуляции разной задержки сети,
// при написании новых тестов и изменении существующих

describe('entityLoader', () => {
    beforeAll(() => {
        console.error = jest.fn(() => {});
    });

    afterAll(() => {
        console.error = originalLog;
    });

    test('Проверяем что лоадер имеет непустое id', () => {
        const loader = entityLoader(apiInstance);
        expect(loader.id).toBeTruthy();
    });

    test('Проверяем подгрузку данных на init', () => {
        const loader = entityLoader(apiInstance, LODER_OPTIONS);
        const saga = function * () {
            yield loader.init();
            const items = yield matchers.select(state => state.items);
            expect(items).toEqual(DATA);
        };

        return expectSaga(saga)
            .withReducer(reducer)
            .run({timeout: requestsTime(2), silenceTimeout: true});
    });

    test('Проверяем что стартовую загрузку можно отключить через loadOnInit', () => {
        const loader = entityLoader(apiInstance, {
            ...LODER_OPTIONS,
            loadOnInit: false
        });

        return expectSaga(loader.init)
            .withReducer(reducer)
            .run({timeout: requestsTime(2), silenceTimeout: true})
            .then(result => {
                expect(result.storeState.items).toHaveLength(0);
            });
    });

    test('Проверяем что параметры из mapOptions доходят до АПИ', () => {
        const filter = {sort: 'desc'};
        const dataFromStore = {bitcoins: 100500};
        const loader = entityLoader(apiInstance, {
            ...LODER_OPTIONS,
            mapOptions: (state, args) => ({...state, ...args})
        });

        return expectSaga(loader.init, filter)
            .withReducer(reducer)
            .withState(dataFromStore)
            .run({timeout: requestsTime(2), silenceTimeout: true})
            .then(result => {
                expect(result.storeState.meta).toEqual({...filter, ...dataFromStore});
            });
    });

    test('Проверяем что параметры из mapPagination доходят до АПИ', () => {
        const loader = entityLoader(apiInstance, {
            ...LODER_OPTIONS,
            mapPagination: ({skip, limit}) => ({offset: skip, pageSize: limit})
        });

        return expectSaga(loader.init)
            .withReducer(reducer)
            .run({timeout: requestsTime(2), silenceTimeout: true})
            .then(result => {
                expect(result.storeState.meta).toHaveProperty('offset');
                expect(result.storeState.meta).toHaveProperty('pageSize');
            });
    });

    test('Проверяем что по умолчанию данные не грузятся повторно', () => {
        const loader = entityLoader(apiInstance, LODER_OPTIONS);
        const saga = function * () {
            yield loader.init();
            yield delay(requestsTime(1));
            yield matchers.put(commonActions.entity.initLoad(EntityCtr));
        };

        return expectSaga(saga)
            .withReducer(reducer)
            .run({timeout: requestsTime(3), silenceTimeout: true})
            .then(result => {
                const {effects} = result;
                const apiCalls = effects.call.filter(e => e.payload.fn === apiInstance.request);
                expect(apiCalls).toHaveLength(1);
            });
    });

    test('Проверяем что отправка запроса реагирует на результат checkIfLoaded', () => {
        const loader = entityLoader(apiInstance, {
            ...LODER_OPTIONS,
            checkIfLoaded: () => false
        });
        const saga = function * () {
            yield loader.init();
            yield delay(requestsTime(1));
            yield matchers.put(commonActions.entity.initLoad(EntityCtr));
        };

        return expectSaga(saga)
            .withReducer(reducer)
            .run({timeout: requestsTime(3), silenceTimeout: true})
            .then(result => {
                const {effects} = result;
                const apiCalls = effects.call.filter(e => e.payload.fn === apiInstance.request);
                expect(apiCalls).toHaveLength(2);
            });
    });

    test('Проверяем что таски убиваются на destroy', () => {
        const loader = entityLoader(apiInstance, {
            ...LODER_OPTIONS,
            checkIfLoaded: () => false
        });
        const saga = function * () {
            yield loader.init();
            yield delay(requestsTime(1));
            yield loader.destroy();
            yield matchers.put(commonActions.entity.initLoad(EntityCtr));
        };

        return expectSaga(saga)
            .withReducer(reducer)
            .run({timeout: requestsTime(3), silenceTimeout: true})
            .then(result => {
                const {effects} = result;
                const apiCalls = effects.call.filter(e => e.payload.fn === apiInstance.request);
                expect(apiCalls).toHaveLength(1);
            });
    });

    test('Проверяем что destroy без init не вызывает ошибок', () => {
        const loader = entityLoader(apiInstance, LODER_OPTIONS);

        return expectSaga(loader.destroy)
            .run({timeout: requestsTime(1), silenceTimeout: true});
    });

    test('Проверяем что опция cancel для initLoad позволяет не дожидаться окончания предыдущего запроса', () => {
        const initCount = 10;
        const loader = entityLoader(apiInstance, {
            ...LODER_OPTIONS,
            checkIfLoaded: () => false
        });
        const saga = function * () {
            yield loader.init();
            for (let i = 0; i < initCount; i++) {
                yield matchers.put(commonActions.entity.initLoad(EntityCtr, null, {cancel: true}));
            }
        };

        return expectSaga(saga)
            .withReducer(reducer)
            .run({timeout: requestsTime(2), silenceTimeout: true})
            .then(result => {
                const {effects} = result;
                const apiCalls = effects.call.filter(e => e.payload.fn === apiInstance.request);
                expect(apiCalls.length).toBe(initCount + 1);
            });
    });

    test('Проверяем что для лоадера создается операция', () => {
        const loader = entityLoader(apiInstance, LODER_OPTIONS);

        return expectSaga(loader.init)
            .withReducer(operationsReducer)
            .run({timeout: requestsTime(2), silenceTimeout: true})
            .then(result => {
                expect(result.storeState).toHaveProperty(loader.id);
            });
    });

    test('Проверяем педжинацию', () => {
        const asIs = v => v;
        const {pageSize} = ENTITY_LOADER_DEFAULTS;
        const loader = entityLoader(apiInstance, {
            ...LODER_OPTIONS,
            checkIfLoaded: result => !result.items.length,
            mapPagination: asIs
        });
        const saga = function * () {
            yield loader.init();
            yield delay(requestsTime(1));
            let items = yield matchers.select(state => state.items);
            expect(items).toHaveLength(pageSize);

            yield matchers.put(commonActions.entity.initLoad(EntityCtr));
            yield delay(requestsTime(1));
            items = yield matchers.select(state => state.items);
            expect(items).toHaveLength(pageSize * 2);
        };

        return expectSaga(saga)
            .withReducer(reducer)
            .run({timeout: requestsTime(3), silenceTimeout: true});
    });

    test('Проверяем что опции автоматически обновляются при истинном autoTrackOptions', () => {
        const mapOptions = jest.fn((state, args) => ({...state, ...args}));
        const loader = entityLoader(apiInstance, {
            ...LODER_OPTIONS,
            autoTrackOptions: true,
            mapOptions
        });
        const saga = function * () {
            yield loader.init();
            yield delay(requestsTime(1));
            yield matchers.put(commonActions.entity.initLoad(EntityCtr));
        };

        return expectSaga(saga)
            .withReducer(reducer)
            .run({timeout: requestsTime(2), silenceTimeout: true})
            .then(result => {
                expect(mapOptions).toHaveBeenCalledTimes(2);
            });
    });

    test('Проверяем что по дефолту опции выставляются только явно', () => {
        const mapOptions = jest.fn((state, args) => ({...state, ...args}));
        const loader = entityLoader(apiInstance, {
            ...LODER_OPTIONS,
            mapOptions
        });
        const saga = function * () {
            yield loader.init();
            yield delay(requestsTime(1));
            yield matchers.put(commonActions.entity.initLoad(EntityCtr));
            expect(mapOptions).toHaveBeenCalledTimes(1);

            yield matchers.put(commonActions.entity.initLoad(EntityCtr, null, {reset: true}));
            yield delay(requestsTime(1));
        };

        return expectSaga(saga)
            .withReducer(reducer)
            .run({timeout: requestsTime(3), silenceTimeout: true})
            .then(() => {
                expect(mapOptions).toHaveBeenCalledTimes(2);
            });
    });

    test('Проверяем что args правильно пробрасываются через initLoad', () => {
        const mapOptions = jest.fn((state, args) => args);
        const loader = entityLoader(apiInstance, {
            ...LODER_OPTIONS,
            mapOptions
        });
        const args = {info: 'info'};
        const saga = function * () {
            yield loader.init();
            yield delay(requestsTime(1));

            yield matchers.put(commonActions.entity.initLoad(EntityCtr, args, {reset: true}));
        };

        return expectSaga(saga)
            .withReducer(reducer)
            .run({timeout: requestsTime(2), silenceTimeout: true})
            .then(result => {
                expect(mapOptions).toHaveLastReturnedWith(args);
            });
    });
});
