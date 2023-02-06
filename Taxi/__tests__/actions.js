import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import createActions from '../actions';
import createApi from '../api';
import {actions as storeActions} from '../reducer';
import {actions as summaryActions} from '../../summary/reducer';
import {routerActions} from 'connected-react-router';

import {getWebviewAuthFromState} from '_common/static/services/help/services/session/selectors';
import {webviewAuthToOptions} from '_common/static/services/help/utils';

const TEST_UID = 'testuid';
jest.mock('uuid/v4', () => () => 'testuid');
const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

const createStoreMock = (chat = {}) => ({
    session: {
        token: 'testtocken'
    },
    help: {
        root: '/help'
    },
    chat,
    config: {}
});

const OPTIONS = {
    getAuthFromState: getWebviewAuthFromState,
    authToOptions: webviewAuthToOptions
};

describe('help', () => {
    describe('chat actions', () => {
        const getActions = transport => createActions(createApi(transport, OPTIONS), OPTIONS);

        it('request должен вызывать нужный экшены при успехе', () => {
            const expectedActions = [storeActions.request(), storeActions.requestSuccess({data: {}})];

            const store = mockStore(createStoreMock());

            return store.dispatch(getActions({post: jest.fn().mockResolvedValue({})}).request()).then(() => {
                expect(store.getActions()).toEqual(expectedActions);
            });
        });

        it('request должен вызывать нужный экшены при ошибке', () => {
            const expectedActions = [storeActions.request(), storeActions.requestError()];

            const store = mockStore(createStoreMock());

            return store.dispatch(getActions({post: jest.fn().mockRejectedValue({})}).request()).catch(() => {
                expect(store.getActions()).toEqual(expectedActions);
            });
        });

        it('sendMessage должен вызывать нужный экшены при успехе', () => {
            const MESSAGE = 'test me';

            const expectedMessage = {
                author: 'user',
                text: MESSAGE,
                type: 'text',
                id: TEST_UID,
                metadata: {
                    attachments: []
                }
            };

            const expectedActions = [
                storeActions.resetInput(),
                storeActions.sendMessage(expectedMessage),
                storeActions.sendMessageSuccess({messageId: expectedMessage.id, data: {}})
            ];

            const store = mockStore(createStoreMock());

            return store.dispatch(getActions({post: jest.fn().mockResolvedValue({})}).sendMessage(MESSAGE)).then(() => {
                expect(store.getActions()).toEqual(expectedActions);
            });
        });

        it('sendMessage должен вызывать нужный экшены при ошибке', () => {
            const MESSAGE = 'test me';

            const expectedMessage = {
                author: 'user',
                text: MESSAGE,
                type: 'text',
                id: TEST_UID,
                metadata: {
                    attachments: []
                }
            };

            const expectedActions = [
                storeActions.resetInput(),
                storeActions.sendMessage(expectedMessage),
                storeActions.sendMessageError(expectedMessage.id)
            ];

            const store = mockStore(createStoreMock());

            return store
                .dispatch(getActions({post: jest.fn().mockRejectedValue({})}).sendMessage(MESSAGE))
                .catch(() => {
                    expect(store.getActions()).toEqual(expectedActions);
                });
        });

        it('retrySendMessage должен вызывать нужный экшены при успехе', () => {
            const MESSAGE = 'test me';

            const expectedMessage = {
                author: 'user',
                text: MESSAGE,
                type: 'text',
                id: TEST_UID
            };

            const expectedActions = [
                storeActions.retrySendMessage(expectedMessage.id),
                storeActions.sendMessageSuccess({messageId: expectedMessage.id, data: {}})
            ];

            const store = mockStore(createStoreMock());

            return store
                .dispatch(getActions({post: jest.fn().mockResolvedValue({})}).retrySendMessage(expectedMessage, 1))
                .then(() => {
                    expect(store.getActions()).toEqual(expectedActions);
                });
        });

        it('retrySendMessage должен вызывать нужный экшены при ошибке', () => {
            const MESSAGE = 'test me';

            const expectedMessage = {
                author: 'user',
                text: MESSAGE,
                type: 'text',
                id: TEST_UID
            };

            const expectedActions = [
                storeActions.retrySendMessage(expectedMessage.id),
                storeActions.sendMessageError(expectedMessage.id)
            ];

            const store = mockStore(createStoreMock());

            return store
                .dispatch(getActions({post: jest.fn().mockRejectedValue({})}).retrySendMessage(expectedMessage, 1))
                .catch(() => {
                    expect(store.getActions()).toEqual(expectedActions);
                });
        });

        it('retrySendMessage должен вызывать нужный экшены при 409 ошибке', () => {
            const MESSAGE = 'test me';

            const expectedMessage = {
                author: 'user',
                text: MESSAGE,
                type: 'text',
                id: TEST_UID
            };

            const expectedActions = [storeActions.retrySendMessage(expectedMessage.id), storeActions.request()];

            const store = mockStore(createStoreMock());

            return store
                .dispatch(
                    getActions({post: jest.fn().mockRejectedValue({status: 409})}).retrySendMessage(expectedMessage, 1)
                )
                .then(() => {
                    expect(store.getActions()).toEqual(expectedActions);
                });
        });

        it('saveCsat должен вызывать нужный экшены при успехе', () => {
            const expectedActions = [
                storeActions.saveCsat(),
                storeActions.saveCsatSuccess(),
                summaryActions.hideChat(),
                routerActions.push({
                    pathname: '/help',
                    search: ''
                })
            ];

            const store = mockStore(createStoreMock({selectedCsatOption: {option_key: 2}}));

            return store.dispatch(getActions({post: jest.fn().mockResolvedValue({})}).saveCsat()).then(() => {
                expect(store.getActions()).toEqual(expectedActions);
            });
        });

        it('saveCsat должен вызывать нужный экшены при ошибке', () => {
            const expectedActions = [storeActions.saveCsat(), storeActions.saveCsatError(TEST_UID)];

            const store = mockStore(createStoreMock({selectedCsatOption: {option_key: 2}}));

            return store.dispatch(getActions({post: jest.fn().mockRejectedValue({})}).saveCsat(1)).catch(() => {
                expect(store.getActions()).toEqual(expectedActions);
            });
        });
    });
});
