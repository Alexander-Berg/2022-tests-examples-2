jest.useFakeTimers();

import {setAuthMailError, changePagePopupVisibility, changeProcessedAccount} from '../actions';
import {SUCCESS_AUTH_LETTER} from '../metrics_constants';
import metrics from '../../metrics';
import checkAuthWithMailStatus from '../checkAuthWithMailStatus';

jest.mock('../actions', () => ({
    setAuthMailError: jest.fn(),
    changePagePopupVisibility: jest.fn(),
    changeProcessedAccount: jest.fn()
}));
jest.mock('../../metrics', () => ({
    send: jest.fn()
}));

Object.defineProperty(global.$, 'ajax', {
    writable: true
});

const {location} = window;

describe('Helpers: mail auth', () => {
    beforeEach(() => {
        delete window.location;
        window.location = {
            href: 'some url',
            reload: jest.fn()
        };
    });

    afterEach(() => {
        setAuthMailError.mockClear();
        changePagePopupVisibility.mockClear();
        metrics.send.mockClear();
        metrics.send.mockClear();
        setAuthMailError.mockClear();
        window.location = location;
    });

    it('should init mail auth', () => {
        const setStoreFn = checkAuthWithMailStatus.setStore;

        checkAuthWithMailStatus.setStore = jest.fn();

        const store = {foo: 'bar'};

        checkAuthWithMailStatus.init(store);

        expect(checkAuthWithMailStatus.setStore).toBeCalled();
        expect(checkAuthWithMailStatus.setStore).toBeCalledWith(store);

        checkAuthWithMailStatus.setStore = setStoreFn;
    });

    it('should start mail auth with params', () => {
        const restartFn = checkAuthWithMailStatus.restart;

        checkAuthWithMailStatus.restart = jest.fn();

        const params = {foo: 'bar'};

        checkAuthWithMailStatus.start(params);

        expect(checkAuthWithMailStatus.restart).toBeCalled();
        expect(checkAuthWithMailStatus.restart).toBeCalledWith(params);

        checkAuthWithMailStatus.restart = restartFn;
    });

    it('should restart mail auth', () => {
        const getStoreFn = checkAuthWithMailStatus.getStore;
        const stopFn = checkAuthWithMailStatus.stop;
        const restartPollgingFn = checkAuthWithMailStatus.restartPolling;

        checkAuthWithMailStatus._interval = 300;
        checkAuthWithMailStatus._stopped = true;

        checkAuthWithMailStatus.getStore = jest.fn(() => ({
            getState: jest.fn(() => ({
                common: {
                    track_id: 'trackId',
                    csrf: 'magicCSRF',
                    retpath: 'retpath'
                },
                auth: {
                    processedAccount: {
                        allowed_auth_methods: ['password', 'magic_link']
                    }
                }
            }))
        }));
        checkAuthWithMailStatus.stop = jest.fn();
        checkAuthWithMailStatus.restartPolling = jest.fn();

        checkAuthWithMailStatus.restart();

        jest.runAllTimers();

        expect(checkAuthWithMailStatus.getStore).toBeCalled();
        expect(checkAuthWithMailStatus.stop).toBeCalled();
        expect(checkAuthWithMailStatus.restartPolling).toBeCalled();
        expect(checkAuthWithMailStatus._interval).toBe(1000);
        expect(global.location.reload).toBeCalled();
        expect(global.location.reload).toBeCalledWith(true);
        expect(checkAuthWithMailStatus._stopped).toBe(false);
        expect(checkAuthWithMailStatus.track_id).toBe('trackId');
        expect(checkAuthWithMailStatus.csrf_token).toBe('magicCSRF');
        expect(checkAuthWithMailStatus.retpath).toBe('retpath');

        checkAuthWithMailStatus.getStore = getStoreFn;
        checkAuthWithMailStatus.stop = stopFn;
        checkAuthWithMailStatus.restartPolling = restartPollgingFn;
    });

    it('should restart mail auth polling', () => {
        const pollFn = checkAuthWithMailStatus.poll;

        checkAuthWithMailStatus.poll = jest.fn();

        checkAuthWithMailStatus._stopped = false;

        checkAuthWithMailStatus.restartPolling();

        jest.runAllTimers();

        expect(checkAuthWithMailStatus.poll).toBeCalled();

        checkAuthWithMailStatus.poll = pollFn;
    });

    it('should not restart mail auth polling', () => {
        const pollFn = checkAuthWithMailStatus.poll;

        checkAuthWithMailStatus.poll = jest.fn();

        checkAuthWithMailStatus._stopped = true;

        checkAuthWithMailStatus.restartPolling();

        jest.runAllTimers();

        expect(checkAuthWithMailStatus.poll).not.toBeCalled();

        checkAuthWithMailStatus.poll = pollFn;
    });

    it('should set and get store', () => {
        const store = {foo: 'bar'};

        checkAuthWithMailStatus.setStore(store);
        const result = checkAuthWithMailStatus.getStore();

        expect(result).toEqual(store);
    });

    it('should stopped polling via flag changes', () => {
        checkAuthWithMailStatus._stopped = false;

        checkAuthWithMailStatus.stopPoll();

        expect(checkAuthWithMailStatus._stopped).toBe(true);
    });

    it('should stop timers and stop polling', () => {
        const stopPollFn = checkAuthWithMailStatus.stopPoll;

        checkAuthWithMailStatus.stopPoll = jest.fn();

        checkAuthWithMailStatus.stop();

        expect(checkAuthWithMailStatus.stopPoll).toBeCalled();

        checkAuthWithMailStatus.stopPoll = stopPollFn;
    });

    it('should polling mail auth status', () => {
        const getStoreFn = checkAuthWithMailStatus.getStore;
        const restartPollgingFn = checkAuthWithMailStatus.restartPolling;

        checkAuthWithMailStatus.getStore = jest.fn(() => ({
            dispatch: jest.fn()
        }));
        checkAuthWithMailStatus.restartPolling = jest.fn();

        global.$.ajax = jest.fn(() => ({
            done: jest.fn((fn) => {
                fn({});
            })
        }));

        checkAuthWithMailStatus.poll();

        expect(checkAuthWithMailStatus.getStore).toBeCalled();
        expect(checkAuthWithMailStatus.restartPolling).toBeCalled();

        checkAuthWithMailStatus.getStore = getStoreFn;
        checkAuthWithMailStatus.restartPolling = restartPollgingFn;
    });

    it('should handle polling mail auth status with success response', () => {
        const getStoreFn = checkAuthWithMailStatus.getStore;
        const restartPollgingFn = checkAuthWithMailStatus.restartPolling;
        const stopFn = checkAuthWithMailStatus.stop;

        checkAuthWithMailStatus.getStore = jest.fn(() => ({
            dispatch: jest.fn()
        }));
        checkAuthWithMailStatus.restartPolling = jest.fn();
        checkAuthWithMailStatus.stop = jest.fn();

        global.$.ajax = jest.fn(() => ({
            done: jest.fn((fn) => {
                fn({status: 'ok', magic_link_confirmed: true, track_id: 'track_id'});
            })
        }));

        checkAuthWithMailStatus.poll();

        expect(checkAuthWithMailStatus.getStore).toBeCalled();
        expect(checkAuthWithMailStatus.restartPolling).not.toBeCalled();
        expect(metrics.send).toBeCalled();
        expect(metrics.send).toBeCalledWith([SUCCESS_AUTH_LETTER]);
        expect(checkAuthWithMailStatus.stop).toBeCalled();
        expect(global.location.href).toBe('/auth/finish/?track_id=track_id&retpath=retpath');

        checkAuthWithMailStatus.getStore = getStoreFn;
        checkAuthWithMailStatus.restartPolling = restartPollgingFn;
        checkAuthWithMailStatus.stop = stopFn;
    });

    it('should handle polling mail auth status with success response and fallback retpath', () => {
        const getStoreFn = checkAuthWithMailStatus.getStore;
        const restartPollgingFn = checkAuthWithMailStatus.restartPolling;
        const stopFn = checkAuthWithMailStatus.stop;

        checkAuthWithMailStatus.getStore = jest.fn(() => ({
            dispatch: jest.fn()
        }));
        checkAuthWithMailStatus.restartPolling = jest.fn();
        checkAuthWithMailStatus.stop = jest.fn();

        global.$.ajax = jest.fn(() => ({
            done: jest.fn((fn) => {
                fn({status: 'ok', magic_link_confirmed: true, track_id: 'track_id'});
            })
        }));

        checkAuthWithMailStatus.retpath = null;

        checkAuthWithMailStatus.poll();

        expect(checkAuthWithMailStatus.getStore).toBeCalled();
        expect(checkAuthWithMailStatus.restartPolling).not.toBeCalled();
        expect(metrics.send).toBeCalled();
        expect(metrics.send).toBeCalledWith([SUCCESS_AUTH_LETTER]);
        expect(checkAuthWithMailStatus.stop).toBeCalled();
        expect(global.location.href).toBe('/auth/finish/?track_id=track_id');

        checkAuthWithMailStatus.getStore = getStoreFn;
        checkAuthWithMailStatus.restartPolling = restartPollgingFn;
        checkAuthWithMailStatus.stop = stopFn;
    });

    it('should handle polling mail auth status with fail response', () => {
        checkAuthWithMailStatus.getStore = jest.fn(() => ({
            dispatch: jest.fn(),
            getState: jest.fn(() => ({
                mailAuth: {
                    isUpdatedAuthLetterStatus: false
                },
                auth: {
                    processedAccount: {
                        uid: 'account.uid',
                        primaryAliasType: 5
                    }
                }
            }))
        }));
        checkAuthWithMailStatus.restartPolling = jest.fn();
        checkAuthWithMailStatus.stop = jest.fn();

        global.$.ajax = jest.fn(() => ({
            done: jest.fn((fn) => {
                fn({errors: ['error.1', 'error.2']});
            })
        }));

        checkAuthWithMailStatus.poll();

        expect(checkAuthWithMailStatus.getStore).toBeCalled();
        expect(metrics.send).not.toBeCalled();
        expect(changePagePopupVisibility).toBeCalledWith(false);
        expect(setAuthMailError).toBeCalled();
        expect(setAuthMailError).toBeCalledWith('error.1');
        expect(checkAuthWithMailStatus.stop).toBeCalled();
    });

    it('should handle polling mail auth status with track.not_found error', () => {
        checkAuthWithMailStatus.getStore = jest.fn(() => ({
            dispatch: jest.fn(),
            getState: jest.fn(() => ({
                mailAuth: {
                    isUpdatedAuthLetterStatus: false,
                    isEnable: true
                },
                auth: {
                    processedAccount: {
                        allowed_auth_methods: ['password', 'magic_link']
                    }
                }
            }))
        }));
        checkAuthWithMailStatus.restartPolling = jest.fn();
        checkAuthWithMailStatus.stop = jest.fn();

        global.$.ajax = jest.fn(() => ({
            done: jest.fn((fn) => {
                fn({errors: ['track.not_found', 'error.2']});
            })
        }));

        checkAuthWithMailStatus.trackNotFoundErrorCount = 0;
        checkAuthWithMailStatus.poll();

        expect(checkAuthWithMailStatus.trackNotFoundErrorCount).toBe(1);
        expect(checkAuthWithMailStatus.getStore).toBeCalled();
        expect(checkAuthWithMailStatus.restartPolling).toBeCalled();
        expect(metrics.send).not.toBeCalled();
        expect(setAuthMailError).not.toBeCalled();
        expect(checkAuthWithMailStatus.stop).not.toBeCalled();
    });
    it('should stop polling and show error when we have more than 5 track errors', () => {
        const getStoreFn = checkAuthWithMailStatus.getStore;
        const stopFn = checkAuthWithMailStatus.stop;

        checkAuthWithMailStatus.getStore = jest.fn(() => ({
            dispatch: jest.fn(),
            getState: jest.fn(() => ({
                mailAuth: {
                    isUpdatedAuthLetterStatus: false
                },
                auth: {
                    processedAccount: {
                        uid: 'account.uid',
                        primaryAliasType: 5
                    }
                }
            }))
        }));
        checkAuthWithMailStatus.restartPolling = jest.fn();
        checkAuthWithMailStatus.stop = jest.fn();

        global.$.ajax = jest.fn(() => ({
            done: jest.fn((fn) => {
                fn({errors: ['track.not_found', 'error.2']});
            })
        }));
        checkAuthWithMailStatus.trackNotFoundErrorCount = 6;

        checkAuthWithMailStatus.poll();

        expect(checkAuthWithMailStatus.getStore).toBeCalled();
        expect(metrics.send).not.toBeCalled();
        expect(setAuthMailError).toBeCalled();
        expect(setAuthMailError).toBeCalledWith('global');
        expect(checkAuthWithMailStatus.restartPolling).not.toBeCalled();
        expect(checkAuthWithMailStatus.stop).toBeCalled();

        checkAuthWithMailStatus.getStore = getStoreFn;
        checkAuthWithMailStatus.stop = stopFn;
    });

    it(
        'should call dispatch of changeProcessedAccount with update list of auth methods if error is ' +
            '"magic_link.invalidated" and value of isUpdatedAuthLetterStatus is false',
        () => {
            checkAuthWithMailStatus.getStore = jest.fn(() => ({
                dispatch: jest.fn(),
                getState: jest.fn(() => ({
                    mailAuth: {
                        isEnabled: true,
                        isUpdatedAuthLetterStatus: false
                    },
                    auth: {
                        processedAccount: {
                            allowed_auth_methods: ['password', 'magic_link']
                        }
                    }
                }))
            }));
            checkAuthWithMailStatus.restartPolling = jest.fn();
            checkAuthWithMailStatus.stop = jest.fn();

            global.$.ajax = jest.fn(() => ({
                done: jest.fn((fn) => {
                    fn({errors: ['magic_link.invalidated']});
                })
            }));

            checkAuthWithMailStatus.poll();

            expect(changeProcessedAccount).toBeCalledWith({allowed_auth_methods: ['password']});
        }
    );
});
