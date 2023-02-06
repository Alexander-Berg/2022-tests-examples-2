import {
    AsyncOperation,
    asyncOperationsReducer,
    getId,
    operation,
    OperationService,
    Service,
} from '@iiiristram/sagun';

import {AnyAction, applyMiddleware, combineReducers, createStore, Reducer, Store} from 'redux';
import createSagaMiddleware from 'redux-saga';
import {call} from 'typed-redux-saga';

import {silentReplace, updateList, updateObject} from '../strategies';

type Item = {
    id: string;
    value: number;
};

// TODO вынести тестовые утилиты в sagun
function getSagaRunner<T extends Reducer<any, AnyAction>>(reducer?: T, initialState?: any) {
    const sagaMiddleware = createSagaMiddleware();
    const store = applyMiddleware(sagaMiddleware)(createStore)(
        reducer || (x => x),
        initialState,
    ) as undefined extends T ? Store<any, AnyAction> : Store<ReturnType<T>, AnyAction>;

    return {run: sagaMiddleware.run, store};
}

const operationService = new OperationService({hash: {}});

class TestService extends Service {
    toString() {
        return 'TestService';
    }

    @operation({
        updateStrategy: silentReplace,
    })
    *replace() {
        return {
            id: '0',
            value: 2,
        };
    }

    @operation({
        updateStrategy: updateList<Item>({
            isSame: (a, b) => a.id === b.id,
            merge: (prev, next) => {
                return {
                    id: next.id,
                    value: (prev?.value || 0) + next.value,
                };
            },
        }),
    })
    *update(id: string) {
        return [
            {
                id,
                value: 2,
            },
        ];
    }

    @operation({
        updateStrategy: updateObject<Item>(),
    })
    *merge(value: number) {
        return {
            value,
        };
    }
}

test('silentReplace', () => {
    const testService = new TestService(operationService);
    const operationId = getId(testService.replace);

    const initialOperation: AsyncOperation<Item> = {
        id: operationId,
        result: {
            id: '0',
            value: 0,
        },
    };

    const {run, store} = getSagaRunner(combineReducers({asyncOperations: asyncOperationsReducer}), {
        asyncOperations: {
            [operationId]: initialOperation,
        },
    });

    const state = store.getState().asyncOperations.get(operationId)?.result as Item;
    expect(state).toEqual(initialOperation.result);

    return run(function* () {
        yield* call(testService.replace);
    })
        .toPromise()
        .then(() => {
            const result = store.getState().asyncOperations.get(operationId)?.result;
            expect(result).toEqual({
                id: '0',
                value: 2,
            });
        });
});

test('updateList', () => {
    const testService = new TestService(operationService);
    const operationId = getId(testService.update);

    const initialOperation: AsyncOperation<Item[]> = {
        id: operationId,
        result: [
            {
                id: '0',
                value: 0,
            },
            {
                id: '1',
                value: 1,
            },
        ],
    };

    const {run, store} = getSagaRunner(combineReducers({asyncOperations: asyncOperationsReducer}), {
        asyncOperations: {
            [operationId]: initialOperation,
        },
    });

    const state = store.getState().asyncOperations.get(operationId)?.result as Item[];
    expect(state).toEqual(initialOperation.result);

    return run(function* () {
        yield* call(testService.update, '1');
    })
        .toPromise()
        .then(() => {
            const result = store.getState().asyncOperations.get(operationId)?.result as Item[];
            expect(result[0]).toEqual(initialOperation.result?.[0]);
            expect(result[1]).toEqual({
                id: '1',
                value: 3,
            });
        });
});

test('updateObject', () => {
    const testService = new TestService(operationService);
    const operationId = getId(testService.merge);

    const initialOperation: AsyncOperation<Item> = {
        id: operationId,
        result: {
            id: '0',
            value: 0,
        },
    };

    const {run, store} = getSagaRunner(combineReducers({asyncOperations: asyncOperationsReducer}), {
        asyncOperations: {
            [operationId]: initialOperation,
        },
    });

    const state = store.getState().asyncOperations.get(operationId)?.result as Item[];
    expect(state).toEqual(initialOperation.result);

    return run(function* () {
        yield* call(testService.merge, 2);
    })
        .toPromise()
        .then(() => {
            const result = store.getState().asyncOperations.get(operationId)?.result as Item;
            expect(result).toEqual({
                id: '0',
                value: 2,
            });
        });
});
