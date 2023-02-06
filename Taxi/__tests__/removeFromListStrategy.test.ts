import {combineReducers} from 'redux';
import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';

import asyncOperationsReducer from '_pkg/reducers/asyncOperations';
import {operation} from '_pkg/sagas/decorators';
import {exact} from '_types/__test__/asserts';
import {AsyncOperation, OperationId} from '_types/common/infrastructure';

import removeFromListStrategy, {createOptions} from '../removeFromListStrategy';

const OPERATION_ID = 'OPERATION_ID';

type City = Partial<CitiesYaml.City>;

type Result = {
    meta: {last: boolean}
    id: string
};

const cities: City[] = (new Array(100)).fill(0).map((zero, index) => ({id: `${index + 1}`}));

const reducer = combineReducers({
    asyncOperations: asyncOperationsReducer
});

const {mergeResults} = createOptions<City>('id');

// tslint:disable-next-line: max-classes-per-file
class TestService {
    @operation({
        id: OPERATION_ID,
        updateStrategy: removeFromListStrategy()
    })
    public static * remove(id: string) {
        return id;
    }

    @operation({
        id: OPERATION_ID,
        updateStrategy: removeFromListStrategy<City[], Result, Result['meta']>({
            idKey: 'id',
            mergeResults: (prev, next) => mergeResults(prev, next?.id),
            mergeMeta: (meta, next) => next?.meta
        })
    })
    public static * removeWithMeta() {
        return {
            meta: {last: false},
            id: '1'
        };
    }
}

describe('removeFromListStrategy', () => {
    test('Стратегия удаляет айтем', () => {
        return expectSaga(function * () {
            yield matchers.call(TestService.remove, '1');
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
                expect(result?.length).toBe(cities.length - 1);
                expect(result?.[0]).toEqual({id: '2'});
            });
    });

    test('Стратегия удаляет несколько айтемов', () => {
        return expectSaga(function * () {
            yield matchers.call(TestService.remove, ['1', '2']);
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
                expect(result?.length).toBe(cities.length - 2);
                expect(result?.[0]).toEqual({id: '3'});
            });
    });

    test('Стратегия удаляет айтемы даже если некоторые id невалидны', () => {
        return expectSaga(function * () {
            yield matchers.call(TestService.remove, ['1', 'xxx']);
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
                expect(result?.length).toBe(cities.length - 1);
                expect(result?.[0]).toEqual({id: '2'});
            });
    });

    test('Стратегия использует опции', () => {
        return expectSaga(function * () {
            yield matchers.call(TestService.removeWithMeta);
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
                expect(result?.length).toBe(cities.length - 1);
                expect(result?.[0]).toEqual({id: '2'});
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
                updateStrategy: removeFromListStrategy({
                    idKey: 'name',
                    mergeResults: (prev, next) => {
                        exact<typeof prev, Res | undefined>(true);
                        exact<typeof next, string | undefined>(true);
                        return prev;
                    }
                })
            })
            public static * method() {
                return '101010';
            }

            @operation({
                id,
                // работает явное указание
                updateStrategy: removeFromListStrategy<Res, number[]>({
                    idKey: 'name',
                    mergeResults: (prev, next) => {
                        exact<typeof prev, Res | undefined>(true);
                        exact<typeof next, number[] | undefined>(true);
                        return prev;
                    }
                })
            })
            public static * method2() {
                return [0];
            }

            @operation({
                // defaults
                updateStrategy: removeFromListStrategy({
                    mergeResults: (prev, next) => {
                        exact<typeof prev, Array<{id: string}> | undefined>(true);
                        exact<typeof next, string | undefined>(true);
                        return prev;
                    }
                })
            })
            public static * method3() {
                return '101010';
            }
        }
    });
});
