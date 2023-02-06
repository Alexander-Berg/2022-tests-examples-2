import {combineReducers} from 'redux';
import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';

import asyncOperationsReducer from '_pkg/reducers/asyncOperations';
import {operation} from '_pkg/sagas/decorators';
import {exact} from '_types/__test__/asserts';
import {AsyncOperation, OperationId} from '_types/common/infrastructure';

import extendListStrategy from '../extendListStrategy';

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

// tslint:disable-next-line: max-classes-per-file
class TestService {
    @operation({
        id: OPERATION_ID,
        updateStrategy: extendListStrategy<City[], City>()
    })
    public static * create() {
        return {id: '101010'} as City;
    }

    @operation({
        id: OPERATION_ID,
        updateStrategy: extendListStrategy<City[]>()
    })
    public static * createArr() {
        return [{id: '101010'}, {id: '111111'}] as City[];
    }

    @operation({
        id: OPERATION_ID,
        updateStrategy: extendListStrategy({
            mergeResults: (prev: City[], next: City) => [next, ...prev]
        })
    })
    public static * prepend() {
        return {id: '111111'} as City;
    }

    @operation({
        id: OPERATION_ID,
        updateStrategy: extendListStrategy<Result['item'][], Result, Result['meta']>({
            mergeResults: (prev, next) => next ? [next.item, ...prev!] : prev,
            mergeMeta: (meta, next) => next?.meta
        })
    })
    public static * createWithtMeta() {
        return {
            meta: {last: false},
            item: {id: '111111'} as City
        };
    }
}

describe('extendListStrategy', () => {
    test('Стратегия дописывает айтем в конец', () => {
        return expectSaga(function * () {
            yield matchers.call(TestService.create);
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
                expect(result?.length).toBe(cities.length + 1);
                expect(result?.[result.length - 1]).toEqual({id: '101010'});
            });
    });

    test('Стратегия дописывает айтемы в конец', () => {
        return expectSaga(function * () {
            yield matchers.call(TestService.createArr);
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
                expect(result?.length).toBe(cities.length + 2);
                expect(result?.[result.length - 1]).toEqual({id: '111111'});
            });
    });

    test('Стратегия использует mergeResults', () => {
        return expectSaga(function * () {
            yield matchers.call(TestService.prepend);
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
                expect(result?.length).toBe(cities.length + 1);
                expect(result?.[0]).toEqual({id: '111111'});
            });
    });

    test('Стратегия использует mergeMeta', () => {
        return expectSaga(function * () {
            yield matchers.call(TestService.createWithtMeta);
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
                const {result, meta}: AsyncOperation<City[]> = runResult.storeState.asyncOperations[OPERATION_ID];
                expect(result?.length).toBe(cities.length + 1);
                expect(result?.[0]).toEqual({id: '111111'});
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
                updateStrategy: extendListStrategy({
                    mergeResults: (prev, next) => {
                        exact<typeof prev, Res | undefined>(true);
                        exact<typeof next, Res | undefined>(true);
                        return next;
                    }
                })
            })
            public static * method() {
                return [{name: '101010'}];
            }

            @operation({
                id,
                // работает явное указание
                updateStrategy: extendListStrategy<Res, Res[number]>({
                    mergeResults: (prev, next) => {
                        exact<typeof prev, Res | undefined>(true);
                        exact<typeof next, Res[number] | undefined>(true);
                        return next ? [...prev!, next] : prev;
                    }
                })
            })
            public static * method2() {
                return {name: '101010'};
            }
        }
    });
});
