jest.mock('../../../../api', () => ({
    request: jest.fn()
}));

import api from '../../../../api';
import {redirectToRetpath, domikIsLoading} from '../../../actions';
import {setErrors, clearErrors} from '../';
import skipAdditionalData from '../skip_additional_data';
import redirectToPasswordRequest from '../redirect_to_password_request';
import submitEmailConfirmationCode from '../submit_email_confirmation_code';
import sendMetrics from '../send_metrics';

jest.mock('../', () => ({
    clearErrors: jest.fn(),
    setErrors: jest.fn()
}));
jest.mock('../../../actions', () => ({
    redirectToRetpath: jest.fn(),
    domikIsLoading: jest.fn()
}));
jest.mock('../skip_additional_data');
jest.mock('../redirect_to_password_request');
jest.mock('../send_metrics');

describe('Action: submitEmailConfirmationCode', () => {
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
            const key = '1234';
            const processedAccountUid = 'processedAccount.uid';
            const defaultAccountUid = 'defaultAccount.uid';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
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
                key,
                csrf_token: 'token',
                track_id: '1234',
                uid: processedAccountUid
            };

            submitEmailConfirmationCode(key)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(3);
            expect(sendMetrics).toBeCalled();
            expect(clearErrors).toBeCalled();
            expect(api.request).toBeCalledWith('email/confirm/by_code', params);
        });

        it('should send api request with default account uid', () => {
            const key = '1234';
            const defaultAccountUid = 'defaultAccount.uid';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
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
                key,
                csrf_token: 'token',
                track_id: '1234',
                uid: defaultAccountUid
            };

            submitEmailConfirmationCode(key)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(3);
            expect(sendMetrics).toBeCalled();
            expect(clearErrors).toBeCalled();
            expect(api.request).toBeCalledWith('email/confirm/by_code', params);
        });

        it('should send api request with empty uid', () => {
            const key = '1234';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                one_domik: {},
                common: {
                    csrf: 'token'
                }
            }));
            const params = {
                key,
                csrf_token: 'token',
                track_id: '1234',
                uid: ''
            };

            submitEmailConfirmationCode(key)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(3);
            expect(sendMetrics).toBeCalled();
            expect(clearErrors).toBeCalled();
            expect(api.request).toBeCalledWith('email/confirm/by_code', params);
        });

        it('should dispatch skip additional data with falsy flag', () => {
            const key = '1234';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                one_domik: {},
                common: {
                    csrf: 'token'
                }
            }));

            submitEmailConfirmationCode(key)(dispatch, getState);

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
            domikIsLoading.mockClear();
        });

        it('should set empty key error', () => {
            const dispatch = jest.fn();

            submitEmailConfirmationCode('')(dispatch);

            expect(dispatch.mock.calls.length).toBe(2);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(setErrors).toBeCalledWith(['key.empty']);
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
            const key = '1234';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                one_domik: {},
                common: {
                    csrf: 'token'
                }
            }));

            submitEmailConfirmationCode(key)(dispatch, getState);

            expect(redirectToPasswordRequest).toBeCalled();
        });

        it('should handle email confirmed error', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.then = function(fn) {
                        fn({status: 'error', errors: ['email.already_confirmed']});
                        return this;
                    };

                    this.catch = function(fn) {
                        fn({status: 'error', errors: ['email.already_confirmed']});
                        return this;
                    };
                };

                return new FakeApi();
            });
            const key = '1234';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                one_domik: {},
                common: {
                    csrf: 'token'
                }
            }));

            submitEmailConfirmationCode(key)(dispatch, getState);

            expect(redirectToRetpath).toBeCalled();
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
            const key = '1234';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                one_domik: {},
                common: {
                    csrf: 'token'
                }
            }));

            submitEmailConfirmationCode(key)(dispatch, getState);

            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(setErrors).toBeCalledWith(['error.1', 'error.2']);
        });
    });
});
