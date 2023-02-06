jest.mock('../../../../api', () => ({
    request: jest.fn()
}));

import approveActualPhone from '../approve_actual_phone';
import skipAdditionalData from '../skip_additional_data';
import redirectToPasswordRequest from '../redirect_to_password_request';
import sendMetrics from '../send_metrics';
import {setErrors} from '../';
import * as api from '../../../../api';

jest.mock('../', () => ({
    clearErrors: jest.fn(),
    setErrors: jest.fn()
}));
jest.mock('../skip_additional_data');
jest.mock('../redirect_to_password_request');
jest.mock('../send_metrics');

describe('Actions: approveActualPhone', () => {
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

        it('should skip additional data request', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                one_domik: {},
                settings: {
                    lang: 'ru'
                },
                common: {
                    csrf: 'token'
                }
            }));

            approveActualPhone('1234')(dispatch, getState);

            expect(sendMetrics).toBeCalled();
            expect(skipAdditionalData).toBeCalledWith('no');
        });
    });

    describe('fail cases', () => {
        it('should redirect on password required page', () => {
            redirectToPasswordRequest.mockImplementation(() => () => {});
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.then = function() {
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
                settings: {
                    lang: 'ru'
                },
                common: {
                    csrf: 'token'
                }
            }));

            approveActualPhone('1234')(dispatch, getState);

            expect(redirectToPasswordRequest).toBeCalled();

            api.request.mockClear();
            redirectToPasswordRequest.mockClear();
        });

        it('should set request errors', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.then = function() {
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
                settings: {
                    lang: 'ru'
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
