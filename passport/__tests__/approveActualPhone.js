jest.mock('../../../api', () => ({
    request: jest.fn()
}));

import approveActualPhone from '../approveActualPhone';
import skipAdditionalData from '../skipAdditionalData';
import redirectToPasswordRequest from '../redirectToPasswordRequest';
import sendMetrics from '../sendAdditionalDataRequestMetrics';
import {setErrors} from '../additionalDataRequestActions';
import * as api from '../../../api';

jest.mock('../additionalDataRequestActions', () => ({
    clearErrors: jest.fn(),
    setErrors: jest.fn()
}));
jest.mock('../skipAdditionalData');
jest.mock('../redirectToPasswordRequest');
jest.mock('../sendAdditionalDataRequestMetrics');

describe('Actions: approveActualPhone', () => {
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

        it('should skip additional data request', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                auth: {},
                settings: {
                    language: 'ru'
                },
                common: {
                    csrf: 'token'
                }
            }));

            approveActualPhone('1234')(dispatch, getState);

            expect(api.request).toBeCalledWith('phone/manage/prolong_valid_v2', {
                csrf_token: 'token',
                display_language: 'ru',
                phone_id: '1234'
            });
            expect(sendMetrics).toBeCalled();
            expect(skipAdditionalData).toBeCalledWith('no');
        });
    });

    describe('fail cases', () => {
        it('should redirect on password required page', () => {
            redirectToPasswordRequest.mockImplementation(() => () => {});
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function() {
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
                auth: {},
                settings: {
                    language: 'ru'
                },
                common: {
                    csrf: 'token'
                }
            }));

            approveActualPhone('1234')(dispatch, getState);

            expect(api.request).toBeCalledWith('phone/manage/prolong_valid_v2', {
                csrf_token: 'token',
                display_language: 'ru',
                phone_id: '1234'
            });
            expect(redirectToPasswordRequest).toBeCalled();

            api.request.mockClear();
            redirectToPasswordRequest.mockClear();
        });

        it('should set request errors', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function() {
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
                auth: {},
                settings: {
                    language: 'ru'
                },
                common: {
                    csrf: 'token'
                }
            }));

            approveActualPhone('1234')(dispatch, getState);

            expect(setErrors).toBeCalledWith(['error.1', 'error.2']);

            api.request.mockClear();
        });
    });
});
