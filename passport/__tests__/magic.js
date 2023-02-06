jest.useFakeTimers();

import {setMagicError} from '../actions';

import showAccounts from '../actions/showAccounts';
import reAuthPasswordSubmit from '../actions/reAuthPasswordSubmit';
import metrics from '../../metrics';

jest.mock('../actions', () => ({
    setMagicError: jest.fn(),
    setLoginError: jest.fn(),
    changeCaptchaState: jest.fn(),
    redirect: jest.fn()
}));
jest.mock('../actions/showAccounts');
jest.mock('../../metrics', () => ({
    goal: jest.fn()
}));
jest.mock('../actions/switchToModeAddingAccount');
jest.mock('../actions/reAuthPasswordSubmit');

import magic from '../magic';

const {location} = window;

describe('Helpers: magic', () => {
    beforeEach(() => {
        delete window.location;
        window.location = {
            origin: 'yandex.ru',
            href: 'https:',
            reload: jest.fn()
        };
    });

    afterEach(() => {
        window.location = location;
    });

    it('should init magic helper', () => {
        const setStoreFn = magic.setStore;

        magic.setStore = jest.fn();

        magic.init();

        expect(magic.setStore).toBeCalled();

        magic.setStore = setStoreFn;
    });

    it('should handle success response', () => {
        const message = {
            origin: 'yandex.ru',
            data: {
                socialAuth: {}
            }
        };

        const getStoreFn = magic.getStore;

        magic.getStore = jest.fn(() => ({
            getState: jest.fn(() => ({
                common: {
                    retpath: 'retpath'
                }
            }))
        }));

        magic.onSuccess(message);

        expect(magic.getStore).toBeCalled();
        expect(showAccounts).not.toBeCalled();

        magic.getStore = getStoreFn;
    });

    it('should handle success response', () => {
        const message = {
            origin: 'yandex.ru',
            data: {}
        };

        const getStoreFn = magic.getStore;

        magic.getStore = jest.fn(() => ({
            getState: jest.fn(() => ({
                common: {
                    retpath: 'retpath'
                }
            }))
        }));

        magic.onSuccess(message);

        expect(magic.getStore).not.toBeCalled();
        expect(showAccounts).not.toBeCalled();

        magic.getStore = getStoreFn;
    });

    it('should handle fallbacks success response', () => {
        window.location = {
            origin: 'some_origin'
        };
        const message = {
            origin: 'yandex.ru',
            data: {
                socialAuth: {}
            }
        };

        const getStoreFn = magic.getStore;

        magic.getStore = jest.fn(() => ({
            getState: jest.fn(() => ({
                common: {
                    retpath: 'retpath'
                }
            }))
        }));

        magic.onSuccess(message);

        expect(magic.getStore).not.toBeCalled();
        expect(showAccounts).not.toBeCalled();

        magic.getStore = jest.fn(() => ({
            getState: jest.fn(() => ({
                common: {}
            })),
            dispatch: jest.fn()
        }));

        window.location = {
            origin: 'yandex.ru'
        };

        magic.onSuccess(message);

        expect(magic.getStore).toBeCalled();
        expect(showAccounts).toBeCalled();

        magic.getStore = getStoreFn;
    });

    it('should start magic succesfuly', () => {
        const restartFn = magic.restart;

        magic.restart = jest.fn();

        magic.start();

        expect(magic.restart).toBeCalled();

        magic.restart = restartFn;
    });

    it('should set stop flag', () => {
        magic._stopped = false;
        magic.stopPoll();

        expect(magic._stopped).toBe(true);
    });

    it('should clear timeouts and stop polling', () => {
        const stopPollFn = magic.stopPoll;

        magic.stopPoll = jest.fn();

        magic.stop();

        expect(magic.stopPoll).toBeCalled();

        magic.stopPoll = stopPollFn;
    });

    it('should restart polling', () => {
        magic._interval = 0;
        magic._stopped = false;

        const pollFn = magic.poll;

        magic.poll = jest.fn();

        magic.restartPolling();

        jest.runAllTimers();

        expect(magic.poll).toBeCalled();

        magic.poll = pollFn;
    });

    it('should not restart polling', () => {
        magic._interval = 0;
        magic._stopped = true;

        const pollFn = magic.poll;

        magic.poll = jest.fn();

        magic.restartPolling();

        jest.runAllTimers();

        expect(magic.poll).not.toBeCalled();

        magic.poll = pollFn;
    });

    it('should set and get store', () => {
        const store = {foo: 'bar'};

        magic.setStore(store);
        const result = magic.getStore();

        expect(result).toEqual(store);
    });

    it('should restart magic helper', () => {
        const restartPollingFn = magic.restartPolling;
        const getStoreFn = magic.getStore;
        const stopFn = magic.stop;

        magic.restartPolling = jest.fn();
        magic.getStore = jest.fn(() => ({
            getState: jest.fn(() => ({
                auth: {
                    magicTrack: 'track',
                    magicCSRF: 'token'
                }
            }))
        }));
        magic.stop = jest.fn();
        magic._interval = 0;

        magic.restart();

        jest.runAllTimers();

        expect(magic._interval).toBe(1000);
        expect(magic.restartPolling).toBeCalled();
        expect(magic.getStore).toBeCalled();
        expect(magic.stop).toBeCalled();
        expect(global.location.reload).toBeCalled();

        magic.getStore = getStoreFn;
        magic.restartPolling = restartPollingFn;
        magic.stop = stopFn;
    });

    it('should polling magic status', () => {
        const restartPollingFn = magic.restartPolling;
        const getStoreFn = magic.getStore;
        const ajaxFn = global.$.ajax;

        magic.restartPolling = jest.fn();
        global.$.ajax = jest.fn(() => ({
            done: jest.fn((fn) => {
                fn({status: 'ok'});
            }),
            fail: jest.fn()
        }));
        magic.getStore = jest.fn(() => ({
            getState: jest.fn(() => ({
                auth: {
                    magicTrack: 'track',
                    magicCSRF: 'token'
                }
            }))
        }));

        magic.poll();

        expect(global.$.ajax).toBeCalled();
        expect(magic.getStore).toBeCalled();
        expect(magic.restartPolling).toBeCalled();

        magic.getStore = getStoreFn;
        magic.restartPolling = restartPollingFn;
        global.$.ajax = ajaxFn;
    });

    it('should polling magic status and finishing', () => {
        const restartPollingFn = magic.restartPolling;
        const getStoreFn = magic.getStore;
        const ajaxFn = global.$.ajax;
        const stopFn = magic.stop;

        magic.stop = jest.fn();
        magic.restartPolling = jest.fn();
        global.$.ajax = jest.fn(() => ({
            done: jest.fn((fn) => {
                fn({status: 'ok', state: 'otp_auth_finished'});
            }),
            fail: jest.fn()
        }));
        magic.getStore = jest.fn(() => ({
            getState: jest.fn(() => ({
                auth: {
                    magicTrack: 'track',
                    magicCSRF: 'token'
                }
            }))
        }));

        magic.poll();

        expect(global.$.ajax).toBeCalled();
        expect(magic.getStore).toBeCalled();
        expect(metrics.goal).toBeCalled();
        expect(magic.stop).toBeCalled();
        expect(magic.restartPolling).not.toBeCalled();

        magic.getStore = getStoreFn;
        magic.restartPolling = restartPollingFn;
        global.$.ajax = ajaxFn;
        magic.stop = stopFn;
    });

    it('should polling magic status and handle errors', () => {
        const restartPollingFn = magic.restartPolling;
        const getStoreFn = magic.getStore;
        const ajaxFn = global.$.ajax;
        const stopFn = magic.stop;

        magic.stop = jest.fn();
        magic.restartPolling = jest.fn();
        global.$.ajax = jest.fn(() => ({
            done: jest.fn((fn) => {
                fn({errors: ['password.not_matched']});
            }),
            fail: jest.fn()
        }));
        magic.getStore = jest.fn(() => ({
            getState: jest.fn(() => ({
                auth: {
                    magicTrack: 'track',
                    magicCSRF: 'token'
                }
            })),
            dispatch: jest.fn()
        }));

        magic.poll();

        expect(global.$.ajax).toBeCalled();
        expect(magic.getStore).toBeCalled();
        expect(magic.stop).toBeCalled();
        expect(setMagicError).toBeCalled();
        expect(reAuthPasswordSubmit).toBeCalled();
        expect(magic.restartPolling).toBeCalled();

        reAuthPasswordSubmit.mockClear();
        magic.restartPolling.mockClear();
        setMagicError.mockClear();

        global.$.ajax = jest.fn(() => ({
            done: jest.fn((fn) => {
                fn({errors: ['track.not_found']});
            }),
            fail: jest.fn()
        }));

        expect(magic.trackNotFoundErrorCount).toBe(0);

        magic.poll();

        expect(magic.trackNotFoundErrorCount).toBe(1);

        reAuthPasswordSubmit.mockClear();
        magic.restartPolling.mockClear();
        setMagicError.mockClear();

        magic.trackNotFoundErrorCount = 6;

        magic.poll();

        expect(reAuthPasswordSubmit).toBeCalled();
        expect(magic.restartPolling).toBeCalled();

        global.$.ajax = jest.fn(() => ({
            done: jest.fn((fn) => {
                fn({errors: ['captcha.required']});
            }),
            fail: jest.fn()
        }));

        magic.stop.mockClear();

        magic.poll();

        expect(magic.stop).toBeCalled();

        reAuthPasswordSubmit.mockClear();
        magic.restartPolling.mockClear();
        setMagicError.mockClear();
        magic.stop.mockClear();

        magic.getStore = getStoreFn;
        magic.restartPolling = restartPollingFn;
        global.$.ajax = ajaxFn;
        magic.stop = stopFn;
    });

    it('should polling magic status and handle connection errors', () => {
        const restartPollingFn = magic.restartPolling;
        const getStoreFn = magic.getStore;
        const ajaxFn = global.$.ajax;
        const stopFn = magic.stop;

        magic.stop = jest.fn();
        magic.restartPolling = jest.fn();
        global.$.ajax = jest.fn(() => ({
            fail: jest.fn((fn) => {
                fn();
            }),
            done: jest.fn()
        }));
        magic.getStore = jest.fn(() => ({
            getState: jest.fn(() => ({
                auth: {
                    magicTrack: 'track',
                    magicCSRF: 'token'
                }
            })),
            dispatch: jest.fn()
        }));

        magic.poll();

        expect(global.$.ajax).toBeCalled();
        expect(magic.getStore).toBeCalled();
        expect(magic.stop).not.toBeCalled();
        expect(setMagicError).not.toBeCalled();
        expect(reAuthPasswordSubmit).not.toBeCalled();
        expect(magic.restartPolling).toBeCalled();

        reAuthPasswordSubmit.mockClear();
        magic.restartPolling.mockClear();
        setMagicError.mockClear();

        global.$.ajax = jest.fn(() => ({
            fail: jest.fn((fn) => {
                fn();
            }),
            done: jest.fn()
        }));

        expect(magic.timeoutErrorCount).toBe(1);

        magic.poll();

        expect(magic.timeoutErrorCount).toBe(2);

        reAuthPasswordSubmit.mockClear();
        magic.restartPolling.mockClear();
        setMagicError.mockClear();

        magic.timeoutFoundErrorCount = 6;

        magic.poll();

        expect(setMagicError).toBeCalled();
        expect(magic.stop).toBeCalled();
        expect(reAuthPasswordSubmit).not.toBeCalled();
        expect(magic.restartPolling).toBeCalled();

        reAuthPasswordSubmit.mockClear();
        magic.restartPolling.mockClear();
        setMagicError.mockClear();
        magic.stop.mockClear();

        magic.getStore = getStoreFn;
        magic.restartPolling = restartPollingFn;
        global.$.ajax = ajaxFn;
        magic.stop = stopFn;
    });
    it.each([['oauth_token.invalid']])('Should dispatch error %s on poll', (error) => {
        const stateMock = {
            getState: jest.fn(() => ({
                auth: {
                    magicTrack: 'track',
                    magicCSRF: 'token'
                }
            })),
            dispatch: jest.fn()
        };
        const ajaxFn = global.$.ajax;

        global.$.ajax = jest.fn(() => ({
            done: jest.fn((fn) => {
                fn({errors: [error]});
            }),
            fail: jest.fn()
        }));

        const restartPollingFn = magic.restartPolling;

        magic.restartPolling = jest.fn();

        magic.init(stateMock);
        magic.poll();

        expect(setMagicError).toBeCalledWith(error);

        setMagicError.mockClear();
        global.$.ajax = ajaxFn;
        magic.restartPolling = restartPollingFn;
    });
});
