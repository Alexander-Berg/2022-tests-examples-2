import {createStore, applyMiddleware, compose} from 'redux';
import thunkMiddleware from 'redux-thunk';
import rootReducer from '@blocks/pushes/ResizeTestPush/reducer';
import {createReduxMiddleware as createNativeMobileApiReduxMiddleware} from '@blocks/authv2/nativeMobileApi';

const devTools =
    typeof window === 'object' &&
    typeof window.devToolsExtension !== 'undefined' &&
    process.env.NODE_ENV !== 'production'
        ? window.devToolsExtension()
        : (f) => f;

export default function(initialState) {
    const middlewares = [thunkMiddleware];

    if (typeof window === 'object' && initialState.am && initialState.am.isAm) {
        middlewares.push(createNativeMobileApiReduxMiddleware(initialState));
    }

    return createStore(rootReducer, initialState, compose(applyMiddleware(...middlewares), devTools));
}
