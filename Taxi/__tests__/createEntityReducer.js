import createEntityReducer from '../createEntityReducer';
import {defaultState} from '../consts';

const intermediateState = {
    items: [1, 2, 3],
    item: {},
    meta: {},
    error: new Error(),
    isRequest: true,
    isRequested: true,
    isCreate: true,
    isUpdate: true,
    isUpdated: false,
    isRemove: true,
    isFind: true,
    isFound: true,
    isLoad: true,
    isLoaded: true,
    isError: true
};

describe('utils:createEntityReducer', () => {
    test('reducer should have actions object', () => {
        const reducer = createEntityReducer({});

        expect(reducer).toHaveProperty('actions');
        expect(reducer.actions).toBeInstanceOf(Object);
    });

    describe('filters reducer', () => {
        const reducer = createEntityReducer({filters: 'TEST'});
        const {actions} = reducer;

        test('filtersSet', () => {
            const filters = {test: 1};
            const state = reducer(undefined, actions.filtersSet(filters));
            expect(state).toEqual({...defaultState, filters});
        });
    });

    describe('request reducer', () => {
        const reducer = createEntityReducer({request: 'TEST'});
        const {actions} = reducer;

        test('request', () => {
            const state = reducer(undefined, actions.request());
            expect(state).toEqual({...defaultState, isRequest: true});
        });

        test('requestSuccess', () => {
            const items = [1];
            const meta = {test: true};
            const options = {testOption: true};
            const state = reducer(undefined, actions.requestSuccess({items, meta, options}));
            expect(state).toEqual({...defaultState, ...options, isRequested: true, isRequest: false, items, meta});
        });

        test('requestError', () => {
            const error = new Error();
            const state = reducer(undefined, actions.requestError({error}));
            expect(state).toEqual({...defaultState, error, isError: true, isRequested: false, isRequest: false});
        });

        test('requestClear', () => {
            const state = reducer(undefined, actions.requestClear());
            expect(state).toEqual(defaultState);
        });

        test('`requestClear` should reset only own part of state', () => {
            const state = reducer(intermediateState, actions.requestClear());
            expect(state).toEqual({
                ...intermediateState,
                isRequest: false,
                isRequested: false,
                isError: false,
                items: [],
                meta: null,
                error: null
            });
        });

        test('`request` action should reset errors set by `requestError`', () => {
            const error = new Error();
            const errorState = reducer(undefined, actions.requestError({error}));
            const finalState = reducer(errorState, actions.request());
            expect(finalState).toEqual({...defaultState, isRequest: true});
        });
    });

    describe('load reducer', () => {
        const reducer = createEntityReducer({load: 'TEST'});
        const {actions} = reducer;

        test('load', () => {
            const state = reducer(undefined, actions.load());
            expect(state).toEqual({...defaultState, isLoad: true});
        });

        test('loadSuccess', () => {
            const options = {testOption: true};
            const meta = {test: true};
            const state = reducer(undefined, actions.loadSuccess({items: [1], options, meta}));
            const updatedState = reducer(state, actions.loadSuccess({items: [2], options, meta}));
            expect(updatedState).toEqual({
                ...defaultState,
                ...options,
                isLoaded: true,
                isLoad: false,
                items: [1, 2],
                meta
            });
        });

        test('loadError', () => {
            const error = new Error();
            const state = reducer(undefined, actions.loadError({error}));
            expect(state).toEqual({...defaultState, error, isError: true, isLoaded: false, isLoad: false});
        });

        test('`load` action should reset errors set by `loadError`', () => {
            const error = new Error();
            const errorState = reducer(undefined, actions.loadError({error}));
            const finalState = reducer(errorState, actions.load());
            expect(finalState).toEqual({...defaultState, isLoad: true});
        });
    });

    describe('create reducer', () => {
        const reducer = createEntityReducer({create: 'TEST'});
        const {actions} = reducer;

        test('create', () => {
            const state = reducer(undefined, actions.create());
            expect(state).toEqual({...defaultState, isCreate: true});
        });

        test('createSuccess', () => {
            const state = reducer({...defaultState, items: [1]}, actions.createSuccess({item: 2}));
            expect(state).toEqual({...defaultState, items: [1, 2], isCreate: false});
        });

        test('createError', () => {
            const error = new Error();
            const state = reducer(undefined, actions.createError({error}));
            expect(state).toEqual({...defaultState, error, isError: true, isCreate: false});
        });

        test('`create` action should reset errors set by `createError`', () => {
            const error = new Error();
            const errorState = reducer(undefined, actions.createError({error}));
            const finalState = reducer(errorState, actions.create());
            expect(finalState).toEqual({...defaultState, isCreate: true});
        });
    });

    describe('update reducer', () => {
        const reducer = createEntityReducer({update: 'TEST'}, {}, {idKey: 'testId'});
        const {actions} = reducer;

        test('update', () => {
            const state = reducer(undefined, actions.update());
            expect(state).toEqual({...defaultState, isUpdate: true, isUpdated: false});
        });

        test('updateSuccess', () => {
            const item = {testId: 1, test: true};
            const state = reducer(
                {...defaultState, items: [{...item, test: false}]},
                actions.updateSuccess({id: 1, item})
            );
            expect(state).toEqual({...defaultState, items: [item], isUpdate: false, isUpdated: true});
        });

        test('updateError', () => {
            const error = new Error();
            const state = reducer(undefined, actions.updateError({error}));
            expect(state).toEqual({...defaultState, error, isError: true, isUpdate: false, isUpdated: false});
        });
    });

    describe('remove reducer', () => {
        const reducer = createEntityReducer({remove: 'TEST'}, {}, {idKey: 'testId'});
        const {actions} = reducer;

        test('remove', () => {
            const state = reducer(undefined, actions.remove());
            expect(state).toEqual({...defaultState, isRemove: true});
        });

        test('removeSuccess', () => {
            const state = reducer({...defaultState, items: [{testId: 1}, {testId: 2}]}, actions.removeSuccess({id: 1}));
            expect(state).toEqual({...defaultState, items: [{testId: 2}], isRemove: false});
        });

        test('removeError', () => {
            const error = new Error();
            const state = reducer(undefined, actions.removeError({error}));
            expect(state).toEqual({...defaultState, error, isError: true, isRemove: false});
        });
    });

    describe('find reducer', () => {
        const reducer = createEntityReducer({find: 'TEST'});
        const {actions} = reducer;

        test('find', () => {
            const state = reducer(undefined, actions.find());
            expect(state).toEqual({...defaultState, isFind: true});
        });

        test('findSuccess', () => {
            const item = {test: true};
            const state = reducer(undefined, actions.findSuccess({item}));
            expect(state).toEqual({...defaultState, isFound: true, isFind: false, item});
        });

        test('findError', () => {
            const error = new Error();
            const state = reducer(undefined, actions.findError({error}));
            expect(state).toEqual({...defaultState, error, isError: true, isFound: false, isFind: false});
        });

        test('findClear', () => {
            const state = reducer(undefined, actions.findClear());
            expect(state).toEqual(defaultState);
        });

        test('`findClear` should reset only own part of state', () => {
            const state = reducer(intermediateState, actions.findClear());
            expect(state).toEqual({
                ...intermediateState,
                isFind: false,
                isFound: false,
                isError: false,
                item: null,
                error: null
            });
        });
    });

    describe('custom reducer', () => {
        test('custom reducer', () => {
            const customAction = {type: 'CUSTOM', payload: {foo: 'BAR'}};
            const reducer = createEntityReducer(
                {request: 'CUSTOM'},
                {
                    custom: (state, {type, payload}) => {
                        if (type === customAction.type) {
                            return {...state, customReducer: true, foo: payload.foo};
                        }

                        return state;
                    }
                }
            );

            const state = reducer(undefined, customAction);
            const updatedState = reducer(state, reducer.actions.request());
            expect(updatedState).toEqual({...defaultState, isRequest: true, customReducer: true, foo: 'BAR'});
        });
    });
});
