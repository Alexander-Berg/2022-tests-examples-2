jest.mock('../../../../api', () => ({
    request: jest.fn()
}));

import api from '../../../../api';
import {setErrors, clearErrors} from '../index';
import skipAdditionalData from '../skip_additional_data';
import redirectToPasswordRequest from '../redirect_to_password_request';
import setSocialProfileAuth from '../set_social_profile_auth';
import {domikIsLoading} from '../../../actions';

jest.mock('../', () => ({
    clearErrors: jest.fn(),
    setErrors: jest.fn()
}));
jest.mock('../../../actions', () => ({
    domikIsLoading: jest.fn()
}));
jest.mock('../skip_additional_data');
jest.mock('../redirect_to_password_request');

describe('Action: setSocialProfileAuth', () => {
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
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                one_domik: {},
                additionalDataRequest: {
                    social: {
                        profile_id: '123'
                    },
                    track_id: '1234'
                },
                common: {
                    csrf: 'token'
                }
            }));
            const params = {
                track_id: '1234',
                csrf_token: 'token',
                profile_id: '123',
                set_auth: 1
            };

            setSocialProfileAuth()(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(2);
            expect(clearErrors).toBeCalled();
            expect(api.request).toBeCalledWith('change_social/profile', params);
        });

        it('should skip additional data request with falsy flag', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                one_domik: {},
                additionalDataRequest: {
                    track_id: '1234',
                    social: {
                        profile_id: '123'
                    }
                },
                common: {
                    csrf: 'token'
                }
            }));

            setSocialProfileAuth()(dispatch, getState);

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
                one_domik: {},
                additionalDataRequest: {
                    track_id: '1234',
                    social: {
                        profile_id: '123'
                    }
                },
                common: {
                    csrf: 'token'
                }
            }));

            setSocialProfileAuth()(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(3);
            expect(redirectToPasswordRequest).toBeCalled();
        });

        it('should handle any api request errors', () => {
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
                one_domik: {},
                additionalDataRequest: {
                    track_id: '1234',
                    social: {
                        profile_id: '123'
                    }
                },
                common: {
                    csrf: 'token'
                }
            }));

            setSocialProfileAuth()(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(4);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(setErrors).toBeCalledWith(['error.1', 'error.2']);
        });
    });
});
