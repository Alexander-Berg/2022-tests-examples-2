import * as redux from 'redux';
import * as router from 'connected-react-router';

jest.mock('redux', () => ({
    createStore: jest.fn(),
    applyMiddleware: jest.fn(),
    compose: jest.fn(),
    combineReducers: jest.fn()
}));
jest.mock('react-router-redux', () => ({
    routerReducer: jest.fn()
}));
jest.mock('connected-react-router', () => ({
    connectRouter: jest.fn(() => jest.fn()),
    routerMiddleware: jest.fn()
}));
jest.mock('redux-thunk');
jest.mock('../../common/reducers');
jest.mock('../reducers/auth');
jest.mock('../reducers/mailAuth');
jest.mock('../reducers/mobileMenu');
jest.mock('@components/Captcha/reducers');

import configureStore, * as helpers from '../configureStore';

describe('Auth: configureStore', () => {
    it('should calls all redux functions', () => {
        global.window.__REDUX_DEVTOOLS_EXTENSION__ = jest.fn();

        configureStore({}, {});

        expect(redux.createStore).toBeCalled();
        expect(router.connectRouter).toBeCalled();
        expect(redux.compose).toBeCalled();
        expect(redux.applyMiddleware).toBeCalled();
        expect(router.routerMiddleware).toBeCalled();
        expect(global.window.__REDUX_DEVTOOLS_EXTENSION__).toBeCalled();

        global.window.__REDUX_DEVTOOLS_EXTENSION__ = undefined;

        redux.compose.mockClear();
        configureStore({}, {});

        expect(redux.createStore).toBeCalled();
        expect(router.connectRouter).toBeCalled();
        expect(redux.compose).toBeCalled();
        expect(redux.applyMiddleware).toBeCalled();
        expect(router.routerMiddleware).toBeCalled();

        const result = redux.compose.mock.calls[0][1]('value');

        expect(result).toBe('value');
    });

    it('should stub reducer', () => {
        let result = helpers.stub({foo: 'bar'});

        expect(result.foo).toBe('bar');

        result = helpers.stub();

        expect(result).toEqual({});
    });
});
