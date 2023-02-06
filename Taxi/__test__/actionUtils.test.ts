import {createPropertySetter, ISimpleAction} from '../actionUtils';

interface State<T = string> {
    value?: T;
    otherValue?: number;
}

const SET_VALUE_ACTION = 'SET_VALUE_ACTION';

const setValue = (payload: string) => ({
    type: SET_VALUE_ACTION,
    payload
});

const INITIAL_PROPERTY_STATE = 'test';

const reducer = createPropertySetter((s: State) => s.value, SET_VALUE_ACTION, {
    initialState: INITIAL_PROPERTY_STATE
});

describe('utils/actionUtils', () => {
    describe('createPropertySetter', () => {
        test('state is undefined', () => {
            const prevState: State | undefined = undefined;

            const nextState = reducer(prevState, {} as any);
            expect(nextState).toEqual({
                value: INITIAL_PROPERTY_STATE
            });
        });

        test('property is undefined', () => {
            const prevState: State = {
                otherValue: 1
            };

            const nextState = reducer(prevState, {} as any);
            expect(nextState).toEqual({
                ...prevState,
                value: INITIAL_PROPERTY_STATE
            });
        });

        test('set property', () => {
            const value = 'value';
            const prevState: State = {
                otherValue: 1
            };

            const nextState = reducer(prevState, setValue(value));
            expect(nextState).toEqual({
                ...prevState,
                value
            });
        });

        test('no initial state', () => {
            const prevState: State = {
                otherValue: 1
            };

            const reducer = createPropertySetter((s: State) => s.value, SET_VALUE_ACTION);

            const nextState = reducer(prevState, {} as any);
            expect(nextState).toBe(prevState);
        });

        test('other actions', () => {
            const prevState: State = {
                otherValue: 1,
                value: 'value'
            };

            const nextState = reducer(prevState, {} as any);
            expect(nextState).toBe(prevState);
        });

        test('custom actions', () => {
            const ADD = 'ADD';
            const REMOVE = 'REMOVE';

            const addAction = (item: string) => ({
                type: ADD,
                payload: item
            });

            const removeAction = (item: string) => ({
                type: REMOVE,
                payload: item
            });

            const prevState: State<string[]> = {
                otherValue: 1
            };

            const reducer = createPropertySetter((s: State<string[]>) => s.value, {
                [ADD]: (value, {payload}: ISimpleAction<string>) => {
                    return payload ? [...value!, payload] : value;
                },
                [REMOVE]: (value, {payload}: ISimpleAction<string>) => {
                    return value?.filter(item => item !== payload);
                }
            }, {
                initialState: []
            });

            const nextState1 = reducer(prevState, addAction('1'));
            expect(nextState1).toEqual({
                otherValue: 1,
                value: ['1']
            });

            const nextState2 = reducer(nextState1, removeAction('1'));
            expect(nextState2).toEqual({
                otherValue: 1,
                value: []
            });
            expect(nextState2).not.toBe(nextState1);
        });
    });
});
