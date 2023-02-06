import combineReducers from '../composeReducers';

describe('utils:createEntityReducer:composeReducers', () => {
    test('should return function', () => {
        expect(combineReducers()).toBeInstanceOf(Function);
    });

    test('should apply reducers sequentially, not losing intermediate state', () => {
        const initialState = {default: true};
        const reducers = [
            (state, action) => action.type === 'TEST' ? {...state, default: false} : state,
            (state, action) => action.type === 'TEST' ? {...state, end: true} : state
        ];
        const action = {type: 'TEST'};
        const reducer = combineReducers(reducers, initialState);

        expect(reducer(undefined, action)).toEqual({default: false, end: true});
    });
});
