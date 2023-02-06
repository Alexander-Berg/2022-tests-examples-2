import {
    AsyncOperation,
    asyncOperationsReducer,
    getId,
    operation,
    OperationService,
    Service,
} from '@iiiristram/sagun';

import {combineReducers} from 'redux';
import {call} from 'typed-redux-saga';

import {getSagaRunner} from '../helpers';
import {
    addToList,
    createPaginationStrategy,
    PaginationArgs,
    removeFromList,
    silentReplace,
    updateList,
    updateObject,
} from '../strategies';

type Item = {
    id: string;
    value: number;
};

const PAGINATION_LIMIT = 2;

const operationService = new OperationService({hash: {}});

class TestService extends Service {
    toString() {
        return 'TestService';
    }

    @operation({
        updateStrategy: silentReplace,
    })
    *replace(val: any) {
        return val;
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

    @operation({
        updateStrategy: addToList<Item>(),
    })
    *addToList(item: Item) {
        return [item];
    }

    @operation({
        updateStrategy: removeFromList<Item>({
            isSame: (a, b) => a.id === b.id,
        }),
    })
    *removeFromList(item: Item) {
        return [item];
    }

    @operation({
        updateStrategy: createPaginationStrategy<Item[]>({limit: PAGINATION_LIMIT}),
    })
    *pagination(args: PaginationArgs, item: Item) {
        return [item];
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
        const val = {
            id: '0',
            value: 2,
        };

        yield* call(testService.replace, val);
        let result = store.getState().asyncOperations.get(operationId)?.result;
        expect(result).toBe(val);

        yield* call(testService.replace, null);
        result = store.getState().asyncOperations.get(operationId)?.result;
        expect(result).toBe(null);
    }).toPromise();
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

test('addToList', () => {
    const testService = new TestService(operationService);
    const operationId = getId(testService.addToList);

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
    const TEST_ITEM = {id: 'ID', value: 10};

    const {run, store} = getSagaRunner(combineReducers({asyncOperations: asyncOperationsReducer}), {
        asyncOperations: {
            [operationId]: initialOperation,
        },
    });

    const state = store.getState().asyncOperations.get(operationId)?.result as Item[];
    expect(state).toEqual(initialOperation.result);

    return run(function* () {
        yield* call(testService.addToList, TEST_ITEM);
    })
        .toPromise()
        .then(() => {
            const result = store.getState().asyncOperations.get(operationId)?.result as Item[];
            expect(result[0]).toEqual(initialOperation.result?.[0]);
            expect(result[2]).toEqual(TEST_ITEM);
        });
});

test('removeFromList', () => {
    const testService = new TestService(operationService);
    const operationId = getId(testService.removeFromList);

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
            {
                id: '2',
                value: 2,
            },
        ],
    };
    const TEST_ITEM = {id: '1', value: 1};

    const {run, store} = getSagaRunner(combineReducers({asyncOperations: asyncOperationsReducer}), {
        asyncOperations: {
            [operationId]: initialOperation,
        },
    });

    const state = store.getState().asyncOperations.get(operationId)?.result as Item[];
    expect(state).toEqual(initialOperation.result);

    return run(function* () {
        yield* call(testService.removeFromList, TEST_ITEM);
    })
        .toPromise()
        .then(() => {
            const result = store.getState().asyncOperations.get(operationId)?.result as Item[];
            expect(result.length).toBe(2);
            expect(result).toEqual([
                {id: '0', value: 0},
                {id: '2', value: 2},
            ]);
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

test('pagination', () => {
    const testService = new TestService(operationService);
    const operationId = getId(testService.pagination);

    const initialOperation: AsyncOperation<Item[]> = {
        id: operationId,
        result: [
            {
                id: '0',
                value: 0,
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
    const newItem: Item = {value: 10, id: 'new'};

    run(function* () {
        yield* call(testService.pagination, {reset: false}, newItem);
        yield* call(testService.pagination, {reset: false}, newItem);
        yield* call(testService.pagination, {reset: false}, newItem);
    })
        .toPromise()
        .then(() => {
            const operation = store.getState().asyncOperations.get(operationId);

            expect(operation?.result).toEqual(
                initialOperation.result?.concat(newItem, newItem, newItem),
            );
            expect((operation as any)?.meta?.limit).toBe(PAGINATION_LIMIT);
            expect((operation as any)?.meta?.skip).toBe(PAGINATION_LIMIT * 2);
        })
        .then(() =>
            run(function* () {
                yield* call(testService.pagination, {reset: true}, newItem);
            }).toPromise(),
        )
        .then(() => {
            const operation = store.getState().asyncOperations.get(operationId);

            expect(operation?.result).toEqual([newItem]);
            expect((operation as any)?.meta?.limit).toBe(PAGINATION_LIMIT);
            expect((operation as any)?.meta?.skip).toBe(0);
        });
});
