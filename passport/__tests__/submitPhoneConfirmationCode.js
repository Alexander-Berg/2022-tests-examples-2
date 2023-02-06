jest.mock('../../../api', () => ({
    request: jest.fn()
}));

import api from '../../../api';
import {domikIsLoading} from '../';
import {setErrors, clearErrors} from '../additionalDataRequestActions';
import skipAdditionalData from '../skipAdditionalData';
import redirectToRetpath from '../redirectToRetpath';
import redirectToPasswordRequest from '../redirectToPasswordRequest';
import submitPhoneConfirmationCode from '../submitPhoneConfirmationCode';
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

describe('Action: submitPhoneConfirmationCode', () => {
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
            const code = '1234';
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
                code,
                csrf_token: 'token',
                track_id: '1234'
            };

            submitPhoneConfirmationCode(code)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(3);
            expect(sendMetrics).toBeCalled();
            expect(clearErrors).toBeCalled();
            expect(api.request).toBeCalledWith('phone/confirm_and_bind_secure/commit_v2', params);
        });

        it('should dispatch skip additional data with falsy flag', () => {
            const code = '1234';
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

            submitPhoneConfirmationCode(code)(dispatch, getState);

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

        it('should set empty code error', () => {
            const dispatch = jest.fn();

            submitPhoneConfirmationCode('')(dispatch);

            expect(dispatch.mock.calls.length).toBe(2);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(setErrors).toBeCalledWith(['code.empty']);
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
            const code = '1234';
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

            submitPhoneConfirmationCode(code)(dispatch, getState);

            expect(redirectToPasswordRequest).toBeCalled();
        });

        it('should handle phone secure confirmed error', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({status: 'error', errors: ['phone_secure.bound_and_confirmed']});
                        return this;
                    };

                    this.fail = function(fn) {
                        fn({status: 'error', errors: ['phone_secure.bound_and_confirmed']});
                        return this;
                    };
                };

                return new FakeApi();
            });
            const code = '1234';
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

            submitPhoneConfirmationCode(code)(dispatch, getState);

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
            const code = '1234';
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

            submitPhoneConfirmationCode(code)(dispatch, getState);

            expect(setErrors).toBeCalledWith(['error.1', 'error.2']);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
        });
    });
});
