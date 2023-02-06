jest.mock('../../../api', () => ({
    request: jest.fn()
}));

import invalidateAuthFromLetter from '../invalidateAuthFromLetter';
import multiStepAuthStart from '../multiStepAuthStart';
import * as api from '../../../api';
import {setAuthMailCancelled, setAuthMailError, updateAuthMailStatus} from '../';
import {AUTH_LETTER_INVALIDATE, AUTH_LETTER_FAIL_AUTH} from '../../metrics_constants';
import metrics from '../../../metrics';

jest.mock('../', () => ({
    setAuthMailCancelled: jest.fn(),
    setAuthMailError: jest.fn(),
    updateAuthMailStatus: jest.fn()
}));
jest.mock('../../../metrics', () => ({
    send: jest.fn()
}));
jest.mock('../multiStepAuthStart');

describe('Action invalidateAuthFromLetter', () => {
    describe('success cases', () => {
        beforeEach(() => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({status: 'ok'});
                        return this;
                    };

                    this.fail = function() {
                        return this;
                    };
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            api.request.mockClear();
            setAuthMailCancelled.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf'
                },
                auth: {
                    processedAccount: {
                        login: 'test-dev',
                        allowed_auth_methods: ['magic_link'],
                        primaryAliasType: 5
                    }
                },
                mailAuth: {
                    mailTrack: 'track'
                }
            }));

            invalidateAuthFromLetter()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/invalidate_magic_letter', {
                csrf_token: 'csrf',
                track_id: 'track'
            });
            expect(setAuthMailCancelled).toBeCalled();
            expect(metrics.send).toBeCalled();
            expect(metrics.send).toBeCalledWith([AUTH_LETTER_INVALIDATE]);
        });

        it('should dispatch multiStepAuthStart if there is no special mailTrack', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf'
                },
                auth: {
                    processedAccount: {
                        login: 'test-dev',
                        allowed_auth_methods: ['magic_link']
                    }
                },
                mailAuth: {
                    mailTrack: ''
                }
            }));

            invalidateAuthFromLetter()(dispatch, getState);
            expect(multiStepAuthStart).toBeCalled();
        });

        it('should dispatch updateAuthMailStatus if there is no special mailTrack', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf'
                },
                auth: {
                    processedAccount: {
                        login: 'test-dev',
                        allowed_auth_methods: ['password']
                    }
                },
                mailAuth: {
                    mailTrack: ''
                }
            }));

            invalidateAuthFromLetter()(dispatch, getState);
            expect(updateAuthMailStatus).toBeCalledWith(true);
        });
    });
    describe('fail cases', () => {
        beforeEach(() => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function() {
                        return this;
                    };

                    this.fail = function(fn) {
                        fn({errors: ['magic_link.invalidated']});
                        return this;
                    };
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            api.request.mockClear();
            setAuthMailCancelled.mockClear();
        });

        it('should handle failed request', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf'
                },
                auth: {
                    processedAccount: {
                        login: 'test-dev'
                    }
                },
                mailAuth: {
                    mailTrack: 'track'
                }
            }));

            invalidateAuthFromLetter()(dispatch, getState);

            expect(setAuthMailError).toBeCalled();
            expect(setAuthMailError).toBeCalledWith('magic_link.invalidated');
            expect(metrics.send).toBeCalled();
            expect(metrics.send).toBeCalledWith([AUTH_LETTER_FAIL_AUTH]);
        });
    });
});
