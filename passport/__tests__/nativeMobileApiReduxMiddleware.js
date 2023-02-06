import {v4} from 'uuid';
import {createStore, compose, applyMiddleware} from 'redux';
import {createReduxMiddleware} from '../nativeMobileApiReduxMiddleware';
import {
    submitAuthSucceed,
    onReady,
    requestNativeSWC,
    onAuthMount,
    startSocialAuth,
    openDebugPage,
    showDebugInfo,
    requestSmsCode,
    amStorePhoneNumber,
    amStoreIcloudToken
} from '@blocks/authv2/actions/nativeMobileApi';
import {Messages} from '@blocks/authv2/nativeMobileApi';

jest.mock('uuid', () => ({
    v4: jest.fn()
}));

function noopReducer(state = {}) {
    return state;
}

function createThunkMiddleware() {
    return function(_ref) {
        const dispatch = (action) => {
            mockDispatch(action);
            return _ref.dispatch(action);
        };
        const getState = _ref.getState;

        return function(next) {
            return function(action) {
                if (typeof action === 'function') {
                    return action(dispatch, getState);
                }

                return next(action);
            };
        };
    };
}

const defaultInitialState = {
    am: {
        isAm: true,
        platform: 'ios'
    }
};

let store;

let postMessageMock;

let mockDispatch;

function prepareStore(initialState = defaultInitialState) {
    postMessageMock = jest.fn();
    mockDispatch = jest.fn();

    window.webkit = {
        messageHandlers: {
            nativeAM: {
                postMessage: postMessageMock
            }
        }
    };

    store = createStore(
        noopReducer,
        initialState,
        compose(applyMiddleware(createThunkMiddleware(), createReduxMiddleware(initialState)))
    );
}

describe('nativeMobileApiReduxMiddleware', function() {
    beforeEach(function() {
        prepareStore();
        v4.mockImplementation(() => {
            return '1';
        });
    });

    afterEach(() => {
        v4.mockClear();
    });

    it('#submitAuthSucceed', function(done) {
        const account = {login: 'test'};
        const password = '123123';

        store.dispatch(submitAuthSucceed(account, password));

        setTimeout(() => {
            expect(postMessageMock).toBeCalledWith(
                expect.objectContaining({
                    data: {
                        login: 'test',
                        password
                    },
                    version: 0,
                    message: Messages.SAVE_LOGIN_CREDENTIALS
                })
            );
            done();
        });
    });

    it('#amStorePhoneNumber', function(done) {
        const phoneNumber = '123123';

        store.dispatch(amStorePhoneNumber(phoneNumber));

        setTimeout(() => {
            expect(postMessageMock).toBeCalledWith(
                expect.objectContaining({
                    data: {
                        phoneNumber
                    },
                    version: 0,
                    message: Messages.STORE_PHONE_NUMBER
                })
            );
            done();
        });
    });

    it('#amStoreIcloudToken', function(done) {
        const icloudToken = 'some token';

        store.dispatch(amStoreIcloudToken(icloudToken));

        setTimeout(() => {
            expect(postMessageMock).toBeCalledWith(
                expect.objectContaining({
                    data: {
                        token: icloudToken
                    },
                    version: 0,
                    message: Messages.STORE_ICLOUD_TOKEN
                })
            );
            done();
        });
    });

    it('#onReady', function(done) {
        store.dispatch(onReady());

        setTimeout(() => {
            expect(postMessageMock).toBeCalledWith(
                expect.objectContaining({
                    data: {
                        status: 'ok'
                    },
                    version: 0,
                    message: Messages.READY
                })
            );
            done();
        });
    });

    it('#requestNativeSWC', function(done) {
        store.dispatch(requestNativeSWC());
        store.dispatch(requestNativeSWC());
        store.dispatch(requestNativeSWC());

        setTimeout(() => {
            expect(postMessageMock).toBeCalledTimes(1);
            expect(postMessageMock).toBeCalledWith(
                expect.objectContaining({
                    data: {},
                    version: 0,
                    message: Messages.REQUEST_SWC
                })
            );
            done();
        });
    });

    it('#onAuthMount', function(done) {
        store.dispatch(onAuthMount());

        setTimeout(() => {
            expect(postMessageMock).toBeCalledWith(
                expect.objectContaining({
                    data: {},
                    version: 0,
                    message: Messages.REQUEST_SWC
                })
            );
            done();
        });
    });

    it('#startSocialAuth', function(done) {
        store.dispatch(startSocialAuth());

        setTimeout(() => {
            expect(postMessageMock).toBeCalledWith(
                expect.objectContaining({
                    data: {},
                    version: 0,
                    message: Messages.SOCIAL_AUTH
                })
            );
            done();
        });
    });

    it('#openDebugPage', function(done) {
        prepareStore({
            ...defaultInitialState,
            am: {
                ...defaultInitialState.am,
                debug: true
            }
        });

        store.dispatch(openDebugPage());

        setTimeout(() => {
            expect(mockDispatch).toBeCalledWith(
                expect.objectContaining({
                    payload: {args: ['/am/debug'], method: 'push'},
                    type: '@@router/CALL_HISTORY_METHOD'
                })
            );
            done();
        });
    });

    it('#showDebugInfo', function(done) {
        store.dispatch(showDebugInfo());

        setTimeout(() => {
            expect(postMessageMock).toBeCalledWith(
                expect.objectContaining({
                    data: {},
                    version: 0,
                    message: Messages.SHOW_DEBUG_INFO
                })
            );
            done();
        });
    });

    it('#requestSmsCode', function(done) {
        store.dispatch(requestSmsCode());

        setTimeout(() => {
            expect(postMessageMock).toBeCalledWith(
                expect.objectContaining({
                    data: {},
                    version: 0,
                    message: Messages.GET_SMS
                })
            );

            done();
        });
    });
});
