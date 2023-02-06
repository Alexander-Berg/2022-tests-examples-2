jest.mock('../../../../api', () => ({
    request: jest.fn()
}));

import api from '../../../../api';
import {domikIsLoading, redirectToRetpath} from '../../../actions';
import {setErrors, clearErrors} from '../';
import skipAdditionalData from '../skip_additional_data';
import redirectToPasswordRequest from '../redirect_to_password_request';
import submitPhoneConfirmationCode from '../submit_phone_confirmation_code';
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

describe('Action: submitPhoneConfirmationCode', () => {
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
            const code = '1234';
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
                code,
                csrf_token: 'token',
                track_id: '1234'
            };

            submitPhoneConfirmationCode(code)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(3);
            expect(sendMetrics).toBeCalled();
            expect(clearErrors).toBeCalled();
            expect(api.request).toBeCalledWith('phone/confirm_and_bind_secure/commit', params);
        });

        it('should dispatch skip additional data with falsy flag', () => {
            const code = '1234';
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
            const code = '1234';
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

            submitPhoneConfirmationCode(code)(dispatch, getState);

            expect(redirectToPasswordRequest).toBeCalled();
        });

        it('should handle phone secure confirmed error', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.then = function(fn) {
                        fn({status: 'error', errors: ['phone_secure.bound_and_confirmed']});
                        return this;
                    };

                    this.catch = function(fn) {
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
                one_domik: {},
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
            const code = '1234';
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

            submitPhoneConfirmationCode(code)(dispatch, getState);

            expect(setErrors).toBeCalledWith(['error.1', 'error.2']);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
        });
    });
});
