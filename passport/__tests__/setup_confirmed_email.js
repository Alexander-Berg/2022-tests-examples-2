jest.mock('../../../../api', () => ({
    request: jest.fn()
}));

import api from '../../../../api';
import {setErrors, clearErrors} from '../';
import skipAdditionalData from '../skip_additional_data';
import sendMetrics from '../send_metrics';
import redirectToPasswordRequest from '../redirect_to_password_request';
import setupConfirmedEmail from '../setup_confirmed_email';

jest.mock('../', () => ({
    clearErrors: jest.fn(),
    setErrors: jest.fn()
}));
jest.mock('../skip_additional_data');
jest.mock('../redirect_to_password_request');
jest.mock('../send_metrics');

describe('Action: setupConfirmedEmail', () => {
    describe('success cases', () => {
        beforeEach(() => {
            skipAdditionalData.mockImplementation(() => () => {});
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.then = function(fn) {
                        fn({status: 'ok'});
                        return this;
                    };

                    this.catch = function() {
                        return this;
                    };
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            api.request.mockClear();
            skipAdditionalData.mockClear();
            sendMetrics.mockClear();
        });

        it('should send api request with valid params', () => {
            const email = 'example@email.ru';
            const processedAccountUid = 'processedAccount.uid';
            const defaultAccountUid = 'defaultAccount.uid';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                one_domik: {
                    processedAccount: {
                        uid: processedAccountUid
                    },
                    defaultAccount: {
                        uid: defaultAccountUid
                    }
                },
                common: {
                    csrf: 'token'
                }
            }));
            const params = {
                email,
                csrf_token: 'token',
                is_safe: 'yes',
                uid: processedAccountUid
            };

            setupConfirmedEmail(email)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(3);
            expect(sendMetrics).toBeCalled();
            expect(clearErrors).toBeCalled();
            expect(api.request).toBeCalledWith('email/setup_confirmed', params);
        });

        it('should send api request with default account uid', () => {
            const email = 'example@email.ru';
            const defaultAccountUid = 'defaultAccount.uid';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                one_domik: {
                    defaultAccount: {
                        uid: defaultAccountUid
                    }
                },
                common: {
                    csrf: 'token'
                }
            }));
            const params = {
                email,
                csrf_token: 'token',
                is_safe: 'yes',
                uid: defaultAccountUid
            };

            setupConfirmedEmail(email)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(3);
            expect(sendMetrics).toBeCalled();
            expect(clearErrors).toBeCalled();
            expect(api.request).toBeCalledWith('email/setup_confirmed', params);
        });

        it('should send api request with empty uid', () => {
            const email = 'example@email.ru';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                one_domik: {},
                common: {
                    csrf: 'token'
                }
            }));
            const params = {
                email,
                csrf_token: 'token',
                is_safe: 'yes',
                uid: ''
            };

            setupConfirmedEmail(email)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(3);
            expect(sendMetrics).toBeCalled();
            expect(clearErrors).toBeCalled();
            expect(api.request).toBeCalledWith('email/setup_confirmed', params);
        });

        it('should dispatch skip additional data request with falsy flag', () => {
            const email = 'example@email.ru';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                one_domik: {},
                common: {
                    csrf: 'token'
                }
            }));

            setupConfirmedEmail(email)(dispatch, getState);

            expect(skipAdditionalData).toBeCalledWith('no');
        });
    });

    describe('fail cases', () => {
        beforeEach(() => {
            redirectToPasswordRequest.mockImplementation(() => () => {});
        });

        afterEach(() => {
            redirectToPasswordRequest.mockClear();
            api.request.mockClear();
        });

        it('should handle password required error', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.then = function(fn) {
                        fn({status: 'error', errors: ['password.required']});
                        return this;
                    };

                    this.catch = function(fn) {
                        fn({status: 'error', errors: ['password.required']});
                        return this;
                    };
                };

                return new FakeApi();
            });
            const email = 'example@email.ru';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                one_domik: {},
                common: {
                    csrf: 'token'
                }
            }));

            setupConfirmedEmail(email)(dispatch, getState);

            expect(redirectToPasswordRequest).toBeCalled();
        });

        it('should handle any errors', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.then = function(fn) {
                        fn({status: 'error', errors: ['error.1', 'error.2']});
                        return this;
                    };

                    this.catch = function(fn) {
                        fn({status: 'error', errors: ['error.1', 'error.2']});
                        return this;
                    };
                };

                return new FakeApi();
            });
            const email = 'example@email.ru';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                one_domik: {},
                common: {
                    csrf: 'token'
                }
            }));

            setupConfirmedEmail(email)(dispatch, getState);

            expect(setErrors).toBeCalledWith(['error.1', 'error.2']);
        });
    });
});
