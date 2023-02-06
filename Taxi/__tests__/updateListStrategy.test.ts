import {combineReducers} from 'redux';
import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';

import asyncOperationsReducer from '_pkg/reducers/asyncOperations';
import {operation} from '_pkg/sagas/decorators';
import {exact} from '_types/__test__/asserts';
import {AsyncOperation, OperationId} from '_types/common/infrastructure';

import updateListStrategy, {createOptions} from '../updateListStrategy';

const OPERATION_ID = 'OPERATION_ID';

type City = Partial<CitiesYaml.City>;

type Result = {
    meta: {last: boolean}
    item: City
};

const cities: City[] = (new Array(100)).fill(0).map((zero, index) => ({id: `${index + 1}`}));

const reducer = combineReducers({
    asyncOperations: asyncOperationsReducer
});

const CITY = {id: '1', disabled: true};

const {mergeResults} = createOptions<City>('id');

// tslint:disable-next-line: max-classes-per-file
class TestService {
    @operation({
        id: OPERATION_ID,
        updateStrategy: updateListStrategy<City[], City>()
    })
    public static * update() {
        return CITY as City;
    }

    @operation({
        id: OPERATION_ID,
        updateStrategy: updateListStrategy<City[]>()
    })
    public static * updateArr() {
        return [CITY] as City[];
    }

    @operation({
        id: OPERATION_ID,
        updateStrategy: updateListStrategy<City[], Result, Result['meta']>({
            idKey: 'id',
            mergeResults: (prev, next) => mergeResults(prev, next?.item),
            mergeMeta: (meta, next) => next?.meta
        })
    })
    public static * updateWithMeta() {
        return {
            meta: {last: false},
            item: CITY as City
        };
    }
}

describe('updateListStrategy', () => {
    test('Стратегия обновляет айтем', () => {
        return expectSaga(function * () {
            yield matchers.call(TestService.update);
        })
            .withReducer(reducer)
            .withState({
                asyncOperations: {
                    [OPERATION_ID]: {
                        result: cities
                    }
                }
            })
            .run()
            .then(runResult => {
                const {result}: AsyncOperation<City[]> = runResult.storeState.asyncOperations[OPERATION_ID];
                expect(result?.length).toBe(cities.length);
                expect(result?.[0]).toEqual(CITY);
            });
    });

    test('Стратегия обновляет массив айтемов', () => {
        return expectSaga(function * () {
            yield matchers.call(TestService.updateArr);
        })
            .withReducer(reducer)
            .withState({
                asyncOperations: {
                    [OPERATION_ID]: {
                        result: cities
                    }
                }
            })
            .run()
            .then(runResult => {
                const {result}: AsyncOperation<City[]> = runResult.storeState.asyncOperations[OPERATION_ID];
                expect(result?.length).toBe(cities.length);
                expect(result?.[0]).toEqual(CITY);
            });
    });

    test('Стратегия использует опции', () => {
        return expectSaga(function * () {
            yield matchers.call(TestService.updateWithMeta);
        })
            .withReducer(reducer)
            .withState({
                asyncOperations: {
                    [OPERATION_ID]: {
                        result: cities
                    }
                }
            })
            .run()
            .then(runResult => {
                const {
                    result,
                    meta
                }: AsyncOperation<City[], any, Result['meta']> = runResult.storeState.asyncOperations[OPERATION_ID];
                expect(result?.length).toBe(cities.length);
                expect(result?.[0]).toEqual(CITY);
                expect(meta).toEqual({last: false});
            });
    });

    test('OperationId types correctly inferred', () => {
        type Res = Array<{name: string}>;
        const id = OPERATION_ID as OperationId<Res>;

        // @ts-ignore
        // tslint:disable-next-line: max-classes-per-file
        class TestService {
            @operation({
                id,
                // автовывод
                updateStrategy: updateListStrategy({
                    idKey: 'name',
                    mergeResults: (prev, next) => {
                        exact<typeof prev, Res | undefined>(true);
                        exact<typeof next, Res | undefined>(true);
                        return [...prev!, ...next!];
                    }
                })
            })
            public static * method() {
                return [{name: '101010'}];
            }

            @operation({
                id,
                // работает явное указание
                updateStrategy: updateListStrategy<Res>({
                    idKey: 'name',
                    mergeResults: (prev, next) => {
                        exact<typeof prev, Res | undefined>(true);
                        exact<typeof next, Res | undefined>(true);
                        return [...prev!, ...next!];
                    }
                })
            })
            public static * method2() {
                return [{name: '101010'}];
            }

            @operation({
                // defaults
                updateStrategy: updateListStrategy({
                    mergeResults: (prev, next) => {
                        exact<typeof prev, Array<{id: string}> | undefined>(true);
                        exact<typeof next, Array<{id: string}> | undefined>(true);
                        return prev;
                    }
                })
            })
            public static * method3() {
                return [{id: '101010'}];
            }
        }
    });
});
