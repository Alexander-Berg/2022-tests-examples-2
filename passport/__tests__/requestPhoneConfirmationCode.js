jest.mock('../../../api', () => ({
    request: jest.fn()
}));

import api from '../../../api';
import requestPhoneConfirmationCode from '../requestPhoneConfirmationCode';
import redirectToRetpath from '../redirectToRetpath';
import {domikIsLoading, changePagePopupVisibility, changePagePopupType} from '../';
import {setErrors, clearErrors, sentPhoneConfirmationCodeSuccess} from '../additionalDataRequestActions';
import redirectToPasswordRequest from '../redirectToPasswordRequest';
import sendMetrics from '../sendAdditionalDataRequestMetrics';

jest.mock('../additionalDataRequestActions', () => ({
    clearErrors: jest.fn(),
    setErrors: jest.fn(),
    sentPhoneConfirmationCodeSuccess: jest.fn()
}));
jest.mock('../', () => ({
    domikIsLoading: jest.fn(),
    changePagePopupVisibility: jest.fn(),
    changePagePopupType: jest.fn()
}));
jest.mock('../redirectToRetpath');
jest.mock('../redirectToPasswordRequest');
jest.mock('../sendAdditionalDataRequestMetrics');

describe('Action: requestPhoneConfirmationCode', () => {
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
            domikIsLoading.mockClear();
            sendMetrics.mockClear();
            changePagePopupVisibility.mockClear();
            changePagePopupType.mockClear();
        });

        it('should send api request with valid params', () => {
            const number = '+71234567890';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                auth: {},
                settings: {
                    language: 'ru'
                },
                common: {
                    csrf: 'token'
                }
            }));
            const params = {
                number,
                track_id: '1234',
                csrf_token: 'token',
                display_language: 'ru',
                isCodeWithFormat: true
            };

            requestPhoneConfirmationCode(number)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(6);
            expect(domikIsLoading).toBeCalled();
            expect(sendMetrics).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(clearErrors).toBeCalled();
            expect(api.request).toBeCalledWith('phone/confirm_and_bind_secure/submit_v2', params);
        });

        it('should dispatch api request success handler', () => {
            const number = '+71234567890';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                auth: {},
                settings: {
                    language: 'ru'
                },
                common: {
                    csrf: 'token'
                }
            }));

            requestPhoneConfirmationCode(number)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(6);
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
                auth: {},
                settings: {
                    language: 'ru'
                },
                common: {
                    csrf: 'token'
                }
            }));

            requestPhoneConfirmationCode(number)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(6);
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
            changePagePopupVisibility.mockClear();
            changePagePopupType.mockClear();
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
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                auth: {},
                settings: {
                    language: 'ru'
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
                    this.done = function(fn) {
                        fn({status: 'error', errors: ['phone.confirmed']});
                        return this;
                    };

                    this.fail = function(fn) {
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
                auth: {},
                settings: {
                    language: 'ru'
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
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                auth: {},
                settings: {
                    language: 'ru'
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
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                auth: {},
                settings: {
                    language: 'ru'
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
