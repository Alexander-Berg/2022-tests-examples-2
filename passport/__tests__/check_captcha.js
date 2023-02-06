jest.mock('@blocks/api', () => ({
    request: jest.fn()
}));

import * as api from '@blocks/api';
import checkCaptcha from '../check_captcha';
import {setErrors, changeCaptchaState} from '../';
import reloadCaptcha from '@components/Captcha/actions/reloadCaptcha';
import {domikIsLoading} from '../../../actions';

jest.mock('../', () => ({
    setErrors: jest.fn(),
    changeCaptchaState: jest.fn()
}));
jest.mock('@components/Captcha/actions/reloadCaptcha');
jest.mock('../../../actions', () => ({
    domikIsLoading: jest.fn()
}));

describe('Action: checkCaptcha', () => {
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
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                one_domik: {},
                additionalDataRequest: {
                    captchaAnswer: 'captcha',
                    track_id: '123'
                },
                common: {
                    csrf: 'token'
                }
            }));
            const params = {
                track_id: '123',
                answer: 'captcha',
                csrf_token: 'token'
            };
            const action = jest.fn();
            const actionArguments = ['arg.1', 'arg.2'];

            checkCaptcha(action, actionArguments)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(2);
            expect(api.request).toBeCalledWith('checkHuman', params);
            expect(changeCaptchaState).toBeCalledWith(false);
            expect(action).toBeCalledWith(actionArguments[0], actionArguments[1]);
        });
    });

    describe('fail cases', () => {
        beforeEach(() => {
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
        });

        afterEach(() => {
            api.request.mockClear();
            domikIsLoading.mockClear();
        });

        it('should set empty captcha answer error', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                one_domik: {},
                additionalDataRequest: {
                    captchaAnswer: '',
                    track_id: '123'
                },
                common: {
                    csrf: 'token'
                }
            }));

            checkCaptcha()(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(1);
            expect(setErrors).toBeCalledWith(['captcha.empty']);
        });

        it('should reload captcha and set request errors', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                one_domik: {},
                additionalDataRequest: {
                    captchaAnswer: 'captcha',
                    track_id: '123'
                },
                common: {
                    csrf: 'token'
                }
            }));

            checkCaptcha()(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(6);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(reloadCaptcha).toBeCalled();
            expect(setErrors).toBeCalledWith(['error.1', 'error.2']);
        });
    });
});
