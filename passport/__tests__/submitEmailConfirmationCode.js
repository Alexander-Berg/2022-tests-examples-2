jest.mock('../../../api', () => ({
    request: jest.fn()
}));

import api from '../../../api';
import {domikIsLoading} from '../';
import {setErrors, clearErrors} from '../additionalDataRequestActions';
import skipAdditionalData from '../skipAdditionalData';
import redirectToPasswordRequest from '../redirectToPasswordRequest';
import submitEmailConfirmationCode from '../submitEmailConfirmationCode';
import redirectToRetpath from '../redirectToRetpath';
import sendMetrics from '../sendAdditionalDataRequestMetrics';

jest.mock('../additionalDataRequestActions', () => ({
    clearErrors: jest.fn(),
    setErrors: jest.fn()
}));
jest.mock('../', () => ({
    domikIsLoading: jest.fn()
}));
jest.mock('../skipAdditionalData');
jest.mock('../redirectToPasswordRequest');
jest.mock('../redirectToRetpath');
jest.mock('../sendAdditionalDataRequestMetrics');

describe('Action: submitEmailConfirmationCode', () => {
    describe('success cases', () => {
        beforeEach(() => {
            skipAdditionalData.mockImplementation(() => () => {});
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
                auth: {
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
            expect(api.request).toBeCalledWith('email/confirm/by_code_v2', params);
        });

        it('should send api request with default account uid', () => {
            const key = '1234';
            const defaultAccountUid = 'defaultAccount.uid';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                auth: {
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
            expect(api.request).toBeCalledWith('email/confirm/by_code_v2', params);
        });

        it('should send api request with empty uid', () => {
            const key = '1234';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                auth: {},
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
            expect(api.request).toBeCalledWith('email/confirm/by_code_v2', params);
        });

        it('should dispatch skip additional data with falsy flag', () => {
            const key = '1234';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                auth: {},
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
                    this.done = function(fn) {
                        fn({status: 'error', errors: ['password.required']});
                        return this;
                    };

                    this.fail = function(fn) {
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
                auth: {},
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
                    this.done = function(fn) {
                        fn({status: 'error', errors: ['email.already_confirmed']});
                        return this;
                    };

                    this.fail = function(fn) {
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
                auth: {},
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
                    this.done = function(fn) {
                        fn({status: 'error', errors: ['error.1', 'error.2']});
                        return this;
                    };

                    this.fail = function(fn) {
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
                auth: {},
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
