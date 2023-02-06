import range from 'lodash/range';
import {combineReducers} from 'redux';
import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';

import asyncOperationsReducer from '_pkg/reducers/asyncOperations';
import {operation} from '_pkg/sagas/decorators';
import {exact} from '_types/__test__/asserts';
import {LoadOperation, OperationId, PaginationArgs, PaginationMeta} from '_types/common/infrastructure';

import createPaginationStrategy from '../paginationStrategy';

type LoadCityOperation = LoadOperation<CitiesYaml.City[]>;

const API_TIMEOUT = 10;
const LIMIT = 20;
const OPERATION_ID = 'OPERATION_ID';
const ARRAY_LENGTH = 5 * LIMIT + 1;

const LIMIT_SAGA = function* () {
    return LIMIT;
};

const cities: Partial<CitiesYaml.City>[] = range(ARRAY_LENGTH).map(index => ({id: `${index + 1}`}));

const reducer = combineReducers({
    asyncOperations: asyncOperationsReducer
});

type State = ReturnType<typeof reducer>;

interface IFakeAPI {
    request({limit, skip}: PaginationMeta): Promise<Partial<CitiesYaml.City>[]>;
}

const getApi = () => {
    class FakeAPI implements IFakeAPI {
        public request = jest.fn(({limit, skip = 0}: PaginationMeta) => {
            const result = cities.slice(skip, skip + limit);

            return new Promise<typeof result>(resolve => {
                setTimeout(() => {
                    resolve(result);
                }, API_TIMEOUT);
            });
        });
    }

    return new FakeAPI();
};

const getService = (api: IFakeAPI, limit: number | Saga<never, number>) => {
    // tslint:disable-next-line: max-classes-per-file
    class TestService {
        @operation({
            id: OPERATION_ID,
            updateStrategy: createPaginationStrategy({
                limit
            })
        })
        public static *method(args?: PaginationArgs) {
            const {meta}: LoadCityOperation = yield matchers.select(
                (state: State) => state.asyncOperations[OPERATION_ID]
            );

            const result: unknown = yield matchers.call(api.request, {...meta});
            return result;
        }
    }

    return TestService;
};

const getCallsTotalCount = (collection: Array<unknown>) => {
    return Math.ceil(collection.length / LIMIT) + 1;
};

describe('createPaginationStrategy', () => {
    describe.each([[LIMIT], [LIMIT_SAGA]])('LIMIT is %p', limit => {
        test('Стратегия подгружает порцию данных в соответствии с limit', () => {
            const api = getApi();
            const TestService = getService(api, limit);

            return expectSaga(function* () {
                yield matchers.call(TestService.method);
            })
                .withReducer(reducer)
                .run()
                .then(runResult => {
                    const {result, meta}: LoadCityOperation = runResult.storeState.asyncOperations[OPERATION_ID];
                    expect(meta?.limit).toEqual(LIMIT);
                    expect(result).toEqual(cities.slice(0, LIMIT));
                });
        });

        test('Стратегия подгружает порцию данных по-странично', () => {
            const api = getApi();
            const TestService = getService(api, limit);

            return expectSaga(function* () {
                yield matchers.call(TestService.method);
                yield matchers.call(TestService.method);
            })
                .withReducer(reducer)
                .run()
                .then(runResult => {
                    const {result}: LoadCityOperation = runResult.storeState.asyncOperations[OPERATION_ID];
                    expect(api.request).toHaveBeenCalledTimes(2);
                    expect(result).toEqual(cities.slice(0, LIMIT * 2));
                });
        });

        test('Стратегия перезапрашивает заново данные на reset', () => {
            const api = getApi();
            const TestService = getService(api, limit);

            return expectSaga(function* () {
                yield matchers.call(TestService.method);
                yield matchers.call(TestService.method);
                yield matchers.call(TestService.method, {reset: true});
            })
                .withReducer(reducer)
                .run()
                .then(runResult => {
                    const {result, meta}: LoadCityOperation = runResult.storeState.asyncOperations[OPERATION_ID];
                    expect(api.request).toHaveBeenCalledTimes(3);
                    expect(meta?.skip).toBe(0);
                    expect(result).toEqual(cities.slice(0, LIMIT));
                });
        });

        test('Стратегия перестает запрашивать данные, после того как приходит пустой массив', () => {
            const api = getApi();
            const TestService = getService(api, limit);

            return expectSaga(function* () {
                for (let i = 0; i < 50; i++) {
                    yield matchers.call(TestService.method);
                }
            })
                .withReducer(reducer)
                .run()
                .then(runResult => {
                    const {result, isBlocked}: LoadCityOperation = runResult.storeState.asyncOperations[OPERATION_ID];
                    expect(api.request).toHaveBeenCalledTimes(getCallsTotalCount(cities));
                    expect(isBlocked).toBe(true);
                    expect(result).toEqual(cities);
                });
        });

        test('Стратегия сбрасывает isBlocked после reset', () => {
            const api = getApi();
            const TestService = getService(api, limit);

            return expectSaga(function* () {
                for (let i = 0; i < 50; i++) {
                    yield matchers.call(TestService.method);
                }

                yield matchers.call(TestService.method, {reset: true});
            })
                .withReducer(reducer)
                .run()
                .then(runResult => {
                    const {result, isBlocked}: LoadCityOperation = runResult.storeState.asyncOperations[OPERATION_ID];
                    expect(isBlocked).toBe(false);
                    expect(api.request).toHaveBeenCalledTimes(getCallsTotalCount(cities) + 1);
                    expect(result).toEqual(cities.slice(0, LIMIT));
                });
        });

        test('OperationId types correctly inferred', () => {
            type Res = {
                cursor: string;
                items: Array<{name: string}>;
            };

            const id = OPERATION_ID as OperationId<Res>;

            // @ts-ignore
            // tslint:disable-next-line: max-classes-per-file
            class TestService {
                @operation({
                    id,
                    // автовывод
                    updateStrategy: createPaginationStrategy({
                        checkIfLoaded: res => !res?.items.length,
                        mergeResults: (prev, next) => {
                            exact<typeof prev, Res | undefined>(true);
                            exact<typeof next, Res | undefined>(true);
                            return next
                                ? {
                                      cursor: next.cursor,
                                      items: [...prev?.items!, ...next.items]
                                  }
                                : prev;
                        }
                    })
                })
                public static *method(args?: PaginationArgs) {
                    return {cursor: 'xxx', items: [{name: '101010'}]};
                }

                @operation({
                    id,
                    // работает явное указание
                    updateStrategy: createPaginationStrategy<Res>({
                        checkIfLoaded: res => !res?.items.length,
                        mergeResults: (prev, next) => {
                            exact<typeof prev, Res | undefined>(true);
                            exact<typeof next, Res | undefined>(true);
                            return next
                                ? {
                                      cursor: next.cursor,
                                      items: [...prev?.items!, ...next.items]
                                  }
                                : prev;
                        }
                    })
                })
                public static *method2(args?: PaginationArgs) {
                    return {cursor: 'xxx', items: [{name: '101010'}]};
                }
            }
        });
    }, 0);
});
