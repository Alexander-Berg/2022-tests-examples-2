jest.mock('../../../../api', () => ({
    request: jest.fn()
}));

import api from '../../../../api';
import requestPhoneConfirmationCode from '../request_phone_confirmation_code';
import {redirectToRetpath, domikIsLoading} from '../../../actions';
import {setErrors, clearErrors, sentPhoneConfirmationCodeSuccess} from '../';
import redirectToPasswordRequest from '../redirect_to_password_request';
import sendMetrics from '../send_metrics';

jest.mock('../', () => ({
    clearErrors: jest.fn(),
    setErrors: jest.fn(),
    sentPhoneConfirmationCodeSuccess: jest.fn()
}));
jest.mock('../../../actions', () => ({
    redirectToRetpath: jest.fn(),
    domikIsLoading: jest.fn()
}));
jest.mock('../redirect_to_password_request');
jest.mock('../send_metrics');

describe('Action: requestPhoneConfirmationCode', () => {
    describe('success cases', () => {
        beforeEach(() => {
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
            domikIsLoading.mockClear();
            sendMetrics.mockClear();
        });

        it('should send api request with valid params', () => {
            const number = '+71234567890';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                one_domik: {},
                settings: {
                    lang: 'ru'
                },
                common: {
                    csrf: 'token'
                }
            }));
            const params = {
                number,
                track_id: '1234',
                csrf_token: 'token',
                display_language: 'ru'
            };

            requestPhoneConfirmationCode(number)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(4);
            expect(domikIsLoading).toBeCalled();
            expect(sendMetrics).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(clearErrors).toBeCalled();
            expect(api.request).toBeCalledWith('phone/confirm_and_bind_secure/submit', params);
        });

        it('should dispatch api request success handler', () => {
            const number = '+71234567890';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                one_domik: {},
                settings: {
                    lang: 'ru'
                },
                common: {
                    csrf: 'token'
                }
            }));

            requestPhoneConfirmationCode(number)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(4);
            expect(domikIsLoading).toBeCalled();
            expect(sendMetrics).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(clearErrors).toBeCalled();
            expect(sentPhoneConfirmationCodeSuccess).toBeCalled();
        });

        it('should send metrics for secure action', () => {
            const number = '+71234567890';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234',
                    action: 'secure'
                },
                one_domik: {},
                settings: {
                    lang: 'ru'
                },
                common: {
                    csrf: 'token'
                }
            }));

            requestPhoneConfirmationCode(number)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(4);
            expect(domikIsLoading).toBeCalled();
            expect(sendMetrics).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(clearErrors).toBeCalled();
            expect(sentPhoneConfirmationCodeSuccess).toBeCalled();
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

        it('should set empty phone error', () => {
            const dispatch = jest.fn();

            requestPhoneConfirmationCode('')(dispatch);

            expect(dispatch.mock.calls.length).toBe(2);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(setErrors).toBeCalledWith(['number.empty']);
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
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                one_domik: {},
                settings: {
                    lang: 'ru'
                },
                common: {
                    csrf: 'token'
                }
            }));
            const number = '+71234567890';

            requestPhoneConfirmationCode(number)(dispatch, getState);

            expect(redirectToPasswordRequest).toBeCalled();
        });

        it('should handle phone confirmed error', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.then = function(fn) {
                        fn({status: 'error', errors: ['phone.confirmed']});
                        return this;
                    };

                    this.catch = function(fn) {
                        fn({status: 'error', errors: ['phone.confirmed']});
                        return this;
                    };
                };

                return new FakeApi();
            });
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                one_domik: {},
                settings: {
                    lang: 'ru'
                },
                common: {
                    csrf: 'token'
                }
            }));
            const number = '+71234567890';

            requestPhoneConfirmationCode(number)(dispatch, getState);

            expect(redirectToRetpath).toBeCalled();
        });

        it('should handle phone secure error', () => {
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
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                one_domik: {},
                settings: {
                    lang: 'ru'
                },
                common: {
                    csrf: 'token'
                }
            }));
            const number = '+71234567890';

            requestPhoneConfirmationCode(number)(dispatch, getState);

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
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                one_domik: {},
                settings: {
                    lang: 'ru'
                },
                common: {
                    csrf: 'token'
                }
            }));

            const number = '+71234567890';

            requestPhoneConfirmationCode(number)(dispatch, getState);

            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(setErrors).toBeCalledWith(['error.1', 'error.2']);
        });
    });
});
