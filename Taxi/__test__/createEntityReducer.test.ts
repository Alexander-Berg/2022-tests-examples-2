import createConsts from '_pkg/utils/createConsts';
import createEntityReducer from '_pkg/utils/createEntityReducer';
import {InitialState} from '_pkg/utils/createEntityReducer';

interface Item {
    gid: string;
    name: string;
}

const initialState: InitialState<Item> = {
    items: [],
    item: null,
    isRequest: false,
    isRequested: false,
    isCreate: false,
    isUpdate: false,
    isRemove: false,
    isFind: false,
    isFound: false,
    isLoad: false,
    isLoaded: false
};

const data = [{gid: '54', name: 'Екатеринбург'}, {gid: '215', name: 'Москва'}];

const PREFIX = 'TEST';

// typeof createEntityReducer<Item> - невалидный синтаксис
// потому делаем такой хелпер, чтобы извлечь из него нужный тип
const fabric = () => createEntityReducer<Item>({});

const createDescription = (prefix: string, description: string) => (
    `(${prefix}) ${description}`
);

const runTests = (reducer: ReturnType<typeof fabric>, testPrefix: string) => {
    test(createDescription(testPrefix, 'Reducer не должен реагировать на чужие actions'), () => {
        expect(reducer(undefined, {type: 'DEV'})).toEqual(initialState);
    });

    describe('request', function () {
        test(createDescription(testPrefix, 'request'), () => {
            const actual = reducer(undefined, reducer.actions.request());

            expect(actual.items).toHaveLength(0);
            expect(actual.isRequest).toBe(true);
            expect(actual.isRequested).toBe(false);
        });

        test(createDescription(testPrefix, 'requestSuccess'), () => {
            const actual = reducer(undefined, reducer.actions.requestSuccess(data));

            expect(actual.items).toHaveLength(data.length);
            expect(actual.items).toEqual(data);
            expect(actual.meta).toEqual({});
            expect(actual.isRequest).toBe(false);
            expect(actual.isRequested).toBe(true);
        });

        test(createDescription(testPrefix, 'requestSuccess with meta'), () => {
            const actual = reducer(undefined, reducer.actions.requestSuccess(data, {limit: 100}));

            expect(actual.items).toHaveLength(data.length);
            expect(actual.items).toEqual(data);
            expect(actual.meta).toEqual({limit: 100});

            expect(actual.isRequest).toBe(false);
            expect(actual.isRequested).toBe(true);
        });

        test(createDescription(testPrefix, 'requestClear'), () => {
            const state = reducer(undefined, reducer.actions.requestSuccess(data, {limit: 100}));
            const actual = reducer(state, reducer.actions.requestClear());

            expect(actual).toEqual(Object.assign({}, initialState, {meta: undefined}));
        });
    });

    describe('remove', function () {
        let state: ReturnType<typeof reducer>;

        test(createDescription(testPrefix, 'remove'), () => {
            state = reducer(undefined, reducer.actions.requestSuccess(data));

            const actual = reducer(state, reducer.actions.remove('215'));

            expect(actual.items).toHaveLength(data.length);
            expect(actual.isRequest).toBe(false);
            expect(actual.isRequested).toBe(true);
            expect(actual.isRemove).toBe(true);
        });

        test(createDescription(testPrefix, 'removeSuccess'), () => {
            const actual = reducer(state, reducer.actions.removeSuccess('215'));

            expect(actual.items).toHaveLength(data.length - 1);
            expect(actual.items).toEqual([{gid: '54', name: 'Екатеринбург'}]);
            expect(actual.isRemove).toBe(false);
        });
    });

    describe('update', function () {
        let state: ReturnType<typeof reducer>;

        test(createDescription(testPrefix, 'update'), () => {
            state = reducer(undefined, reducer.actions.requestSuccess(data));

            const actual = reducer(state, reducer.actions.update('215'));

            expect(actual.items).toHaveLength(data.length);
            expect(actual.isRequest).toBe(false);
            expect(actual.isRequested).toBe(true);
            expect(actual.isUpdate).toBe(true);
        });

        test(createDescription(testPrefix, 'updateSuccess'), () => {
            const actual = reducer(state, reducer.actions.updateSuccess('215', {gid: '215', name: 'Москва-красна'}));

            expect(actual.items).toHaveLength(data.length);
            expect(actual.items).toEqual([{gid: '54', name: 'Екатеринбург'}, {gid: '215', name: 'Москва-красна'}]);
            expect(actual.isUpdate).toBe(false);
        });
    });

    describe('find', function () {
        let state: ReturnType<typeof reducer>;

        test(createDescription(testPrefix, 'find'), () => {
            state = reducer(undefined, reducer.actions.requestSuccess(data));

            const actual = reducer(state, reducer.actions.find('215'));

            expect(actual.items).toHaveLength(data.length);
            expect(actual.isFind).toBe(true);
            expect(actual.isFound).toBe(false);
        });

        test(createDescription(testPrefix, 'findSuccess'), () => {
            const actual = reducer(state, reducer.actions.findSuccess('215', {gid: '215', name: 'Москва-красна'}));

            expect(actual.items).toHaveLength(data.length);
            expect(actual.item).toEqual({gid: '215', name: 'Москва-красна'});
            expect(actual.isFind).toBe(false);
            expect(actual.isFound).toBe(true);
        });
    });
};

describe('utils/createEntityReducer', function () {
    describe('Проверяем редюссер созданный с кастомными экшенами', function () {
        const constants = createConsts(PREFIX)({
            REQUEST: null,
            REQUEST_SUCCESS: null,
            REQUEST_ERROR: null,
            REQUEST_CLEAR: null,

            REMOVE: null,
            REMOVE_SUCCESS: null,
            REMOVE_ERROR: null,

            UPDATE: null,
            UPDATE_SUCCESS: null,
            UPDATE_ERROR: null,

            FIND: null,
            FIND_SUCCESS: null,
            FIND_ERROR: null
        });

        const reducer = createEntityReducer<Item>({
            request: [constants.REQUEST, constants.REQUEST_SUCCESS, constants.REQUEST_ERROR, constants.REQUEST_CLEAR],
            remove: [constants.REMOVE, constants.REMOVE_SUCCESS, constants.REMOVE_ERROR],
            update: [constants.UPDATE, constants.UPDATE_SUCCESS, constants.UPDATE_ERROR],
            find: [constants.FIND, constants.FIND_SUCCESS, constants.FIND_ERROR]
        }, {}, {idKey: 'gid'});

        runTests(reducer, 'Custom actions');
    });

    describe('Проверяем редюссер созданный с автогенерированными экшенами', function () {
        const reducer = createEntityReducer<Item>(`${PREFIX}_AUTO`, {}, {idKey: 'gid'});
        runTests(reducer, 'Autogenerated actions');
    });
});
