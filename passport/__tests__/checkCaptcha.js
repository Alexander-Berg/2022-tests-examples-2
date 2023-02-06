jest.mock('@blocks/api', () => ({
    request: jest.fn()
}));

import * as api from '@blocks/api';
import checkCaptcha from '../checkCaptcha';
import {setCaptchaError, changeCaptchaState, domikIsLoading} from '../';
import reloadCaptcha from '@components/Captcha/actions/reloadCaptcha';

jest.mock('../', () => ({
    setCaptchaError: jest.fn(),
    changeCaptchaState: jest.fn(),
    domikIsLoading: jest.fn()
}));
jest.mock('@components/Captcha/actions/reloadCaptcha');

describe('Action: checkCaptcha', () => {
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
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                auth: {
                    form: {
                        captcha_answer: 'captcha'
                    }
                },
                common: {
                    csrf: 'token',
                    track_id: '123'
                },
                captcha: {
                    trackId: '123'
                }
            }));
            const params = {
                track_id: '123',
                answer: 'captcha',
                csrf_token: 'token'
            };
            const action = jest.fn();
            const actionArguments = ['arg.1', 'arg.2'];

            checkCaptcha({action, actionArguments})(dispatch, getState);

            expect(api.request).toBeCalledWith('checkHuman', params);
            expect(changeCaptchaState).toBeCalledWith(false);
            expect(action).toBeCalledWith(actionArguments[0], actionArguments[1]);
        });
    });

    describe('fail cases', () => {
        beforeEach(() => {
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
        });

        afterEach(() => {
            api.request.mockClear();
            domikIsLoading.mockClear();
        });

        it('should set empty captcha answer error', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                auth: {
                    form: {
                        captcha_answer: ''
                    }
                },
                common: {
                    csrf: 'token',
                    track_id: '123'
                },
                captcha: {
                    trackId: '123'
                }
            }));

            checkCaptcha()(dispatch, getState);
            expect(setCaptchaError).toBeCalledWith('captcha.empty');
        });

        it('should reload captcha and set request errors', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                auth: {
                    form: {
                        captcha_answer: 'captcha'
                    }
                },
                common: {
                    csrf: 'token',
                    track_id: '123'
                },
                captcha: {
                    trackId: null
                }
            }));

            checkCaptcha()(dispatch, getState);

            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(reloadCaptcha).toBeCalled();
            expect(setCaptchaError).toBeCalledWith(['error.1', 'error.2']);
        });
    });
});
