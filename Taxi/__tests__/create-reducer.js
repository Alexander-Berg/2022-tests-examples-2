import createReducer from '../create-reducer';

describe('utils:createReducer', () => {
    const initialState = {
        test: null,
        error: null
    };
    const stateTransformers = {
        TEST: (state, action) => ({
            ...state,
            test: action.payload
        })
    };
    const action = {
        type: 'TEST',
        payload: 'test'
    };
    test('Созданный редюсер должен возвращать правильный стейт', () => {
        const reducer = createReducer(initialState, stateTransformers);
        expect(reducer(undefined, action)).toEqual({
            test: 'test',
            error: null
        });
    });

    test('Экшны неизвестного типа должны возвращать неизмененный стей', () => {
        const reducer = createReducer(initialState, stateTransformers);
        expect(reducer(undefined, {type: 'UNKNOWN'})).toEqual(initialState);
    });

    test('Неизмененные значения стейта должны сохраняться, даже если они не возвращаются из трансформера', () => {
        const stateTransformers = {
            TEST: (state, action) => ({
                test: action.payload
            })
        };
        const reducer = createReducer(initialState, stateTransformers);
        expect(reducer({...initialState, foo: 'bar'}, action)).toEqual({test: 'test', foo: 'bar', error: null});
    });

    test('При merge == false не происходит объединение текущего state с тем что вернул трансформер', () => {
        const stateTransformers = {
            TEST: (state, action) => ({
                test: action.payload
            })
        };
        const reducer = createReducer(initialState, stateTransformers, {merge: false});
        expect(reducer({...initialState}, action)).toEqual({test: 'test'});
    });
});
