jest.mock('../../../api', () => ({
    request: jest.fn()
}));

import api from '../../../api';
import requestEmailConfirmationCode from '../requestEmailConfirmationCode';
import {changePagePopupType, changePagePopupVisibility, domikIsLoading} from '../';
import {setErrors, clearErrors, sentEmailConfirmationCodeSuccess} from '../additionalDataRequestActions';
import redirectToPasswordRequest from '../redirectToPasswordRequest';
import redirectToRetpath from '../redirectToRetpath';
import sendMetrics from '../sendAdditionalDataRequestMetrics';

jest.mock('../additionalDataRequestActions', () => ({
    clearErrors: jest.fn(),
    setErrors: jest.fn(),
    sentEmailConfirmationCodeSuccess: jest.fn()
}));
jest.mock('../', () => ({
    domikIsLoading: jest.fn(),
    changePagePopupType: jest.fn(),
    changePagePopupVisibility: jest.fn()
}));
jest.mock('../redirectToPasswordRequest');
jest.mock('../redirectToRetpath');
jest.mock('../sendAdditionalDataRequestMetrics');

describe('Action: requestEmailConfirmationCode', () => {
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
            changePagePopupType.mockClear();
            changePagePopupVisibility.mockClear();
        });

        it('should send api request with valid params', () => {
            const email = 'example@email.ru';
            const profileUrl = '/profile';
            const defaultAccountUid = 'defaultAccount.uid';
            const processedAccountUid = 'processedAccount.uid';

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
                    profile_url: profileUrl,
                    csrf: 'token'
                }
            }));
            const params = {
                email,
                track_id: '1234',
                csrf_token: 'token',
                validator_ui_url: profileUrl,
                retpath: profileUrl,
                code_only: 'yes',
                uid: processedAccountUid
            };

            requestEmailConfirmationCode(email)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(6);
            expect(clearErrors).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(sendMetrics).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(api.request).toBeCalledWith('email/send_confirmation_email_v2', params);
        });

        it('should send api request with default account uid', () => {
            const email = 'example@email.ru';
            const profileUrl = '/profile';
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
                    profile_url: profileUrl,
                    csrf: 'token'
                }
            }));
            const params = {
                email,
                track_id: '1234',
                csrf_token: 'token',
                validator_ui_url: profileUrl,
                retpath: profileUrl,
                code_only: 'yes',
                uid: defaultAccountUid
            };

            requestEmailConfirmationCode(email)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(6);
            expect(clearErrors).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(sendMetrics).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(api.request).toBeCalledWith('email/send_confirmation_email_v2', params);
        });

        it('should send api request with empty uid', () => {
            const email = 'example@email.ru';
            const profileUrl = '/profile';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                auth: {},
                common: {
                    profile_url: profileUrl,
                    csrf: 'token'
                }
            }));
            const params = {
                email,
                track_id: '1234',
                csrf_token: 'token',
                validator_ui_url: profileUrl,
                retpath: profileUrl,
                code_only: 'yes',
                uid: ''
            };

            requestEmailConfirmationCode(email)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(6);
            expect(clearErrors).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(sendMetrics).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(api.request).toBeCalledWith('email/send_confirmation_email_v2', params);
        });

        it('should dispatch api request success handler', () => {
            const email = 'example@email.ru';
            const profileUrl = '/profile';
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                auth: {},
                common: {
                    profile_url: profileUrl,
                    csrf: 'token'
                }
            }));

            requestEmailConfirmationCode(email)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(6);
            expect(domikIsLoading).toBeCalled();
            expect(sendMetrics).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(clearErrors).toBeCalled();
            expect(sentEmailConfirmationCodeSuccess).toBeCalled();
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
            changePagePopupType.mockClear();
            changePagePopupVisibility.mockClear();
        });

        it('should set empty email error', () => {
            const dispatch = jest.fn();

            requestEmailConfirmationCode('')(dispatch);

            expect(dispatch.mock.calls.length).toBe(2);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(setErrors).toBeCalledWith(['email.empty']);
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
                common: {
                    profile_url: '/profile',
                    csrf: 'token'
                }
            }));

            requestEmailConfirmationCode('example@email.ru')(dispatch, getState);

            expect(redirectToPasswordRequest).toBeCalled();
        });

        it('should handle email already confirmed error', () => {
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
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                auth: {},
                common: {
                    profile_url: '/profile',
                    csrf: 'token'
                }
            }));

            requestEmailConfirmationCode('example@email.ru')(dispatch, getState);

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
                common: {
                    profile_url: '/profile',
                    csrf: 'token'
                }
            }));

            requestEmailConfirmationCode('example@email.ru')(dispatch, getState);

            expect(setErrors).toBeCalledWith(['error.1', 'error.2']);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
        });
    });
});
