jest.mock('@blocks/api', () => ({
    request: jest.fn()
}));

import multiStepAuthCommitPassword from '../multiStepAuthCommitPassword';
// import {getMetricsHeader} from '../multiStepAuthCommitPassword';
import * as api from '@blocks/api';
import {domikIsLoading, setPasswordError, changeCaptchaState, updatePasswordValue} from '../';
import reloadCaptcha from '@components/Captcha/actions/reloadCaptcha';
import changeNativeInputValue from '../changeNativeInputValue';
import {SEND_AUTH_FORM, SEND_AUTH_FORM_SUCCESS, SEND_AUTH_FORM_ERROR, SUCCESS_AUTH_GOAL} from '../../metrics_constants';
import metrics from '@blocks/metrics';
import additionalDataAsk from '../additionalDataAsk';
import {NATIVE_MOBILE_API_OUTGOING_ACTIONS} from '@blocks/authv2/actions/nativeMobileApi';

jest.mock('../', () => ({
    domikIsLoading: jest.fn(),
    setPasswordError: jest.fn(),
    changeCaptchaState: jest.fn(),
    updatePasswordValue: jest.fn()
}));
jest.mock('../changeNativeInputValue');
jest.mock('@components/Captcha/actions/reloadCaptcha');
jest.mock('@blocks/metrics', () => ({
    goal: jest.fn(),
    send: jest.fn()
}));
jest.mock('../additionalDataAsk');

describe('Actions: multiStepAuthCommitPassword', () => {
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
            api.default.setCsrfToken = jest.fn();
        });

        afterEach(() => {
            api.request.mockClear();
            domikIsLoading.mockClear();
            setPasswordError.mockClear();
            changeCaptchaState.mockClear();
            updatePasswordValue.mockClear();
            reloadCaptcha.mockClear();
            metrics.send.mockClear();
            metrics.goal.mockClear();
            additionalDataAsk.mockClear();
            changeNativeInputValue.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const state = {
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    retpath: 'retpath',
                    csrf: 'csrf'
                },
                auth: {
                    form: {
                        isForceOTP: false
                    },
                    processedAccount: {
                        allowed_auth_methods: ['password'],
                        preferred_auth_method: 'password'
                    }
                },
                social: {
                    providers: [{id: 1, data: {code: 'vk'}}]
                }
            };
            const getState = jest.fn(() => state);

            const password = 'password';

            multiStepAuthCommitPassword(password)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_password', {
                track_id: 'track',
                csrf_token: 'csrf',
                password,
                retpath: 'retpath'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(1);
            expect(domikIsLoading).toBeCalledWith(true);
            expect(metrics.goal).toBeCalled();
            expect(metrics.goal).toBeCalledWith(SUCCESS_AUTH_GOAL);
            expect(metrics.send).toBeCalled();
            expect(metrics.send.mock.calls[0][0][1]).toBe(SEND_AUTH_FORM);
            expect(metrics.send.mock.calls[0][0][2]).toBe(SEND_AUTH_FORM_SUCCESS);
            expect(updatePasswordValue).not.toBeCalled();
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
        });

        it('should send api request with valid params and without additional data request', () => {
            const dispatch = jest.fn();
            const state = {
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    retpath: 'retpath',
                    csrf: 'csrf'
                },
                auth: {
                    form: {
                        isForceOTP: false
                    },
                    processedAccount: {
                        allowed_auth_methods: ['password'],
                        preferred_auth_method: 'password'
                    }
                },
                social: {
                    providers: [{id: 1, data: {code: 'vk'}}]
                }
            };
            const getState = jest.fn(() => state);

            multiStepAuthCommitPassword.getMetricsHeader = jest.fn();

            const password = 'password';

            multiStepAuthCommitPassword(password)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_password', {
                track_id: 'track',
                csrf_token: 'csrf',
                password,
                retpath: 'retpath'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(true);
            expect(metrics.goal).toBeCalled();
            expect(metrics.goal).toBeCalledWith(SUCCESS_AUTH_GOAL);
            expect(metrics.send).toBeCalled();
            expect(metrics.send.mock.calls[0][0][1]).toBe(SEND_AUTH_FORM);
            expect(metrics.send.mock.calls[0][0][2]).toBe(SEND_AUTH_FORM_SUCCESS);
            expect(updatePasswordValue).not.toBeCalled();
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
        });

        it('should fallback retpath param to profile url ', () => {
            const dispatch = jest.fn();
            const state = {
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    csrf: 'csrf'
                },
                auth: {
                    form: {
                        isForceOTP: false
                    },
                    processedAccount: {
                        allowed_auth_methods: ['password'],
                        preferred_auth_method: 'password'
                    }
                },
                social: {
                    providers: [{id: 1, data: {code: 'vk'}}]
                }
            };
            const getState = jest.fn(() => state);

            const password = 'password';

            multiStepAuthCommitPassword(password)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_password', {
                track_id: 'track',
                csrf_token: 'csrf',
                password,
                retpath: '/profile'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(true);
            expect(metrics.goal).toBeCalled();
            expect(metrics.goal).toBeCalledWith(SUCCESS_AUTH_GOAL);
            expect(metrics.send).toBeCalled();
            expect(metrics.send.mock.calls[0][0][1]).toBe(SEND_AUTH_FORM);
            expect(metrics.send.mock.calls[0][0][2]).toBe(SEND_AUTH_FORM_SUCCESS);
            expect(updatePasswordValue).not.toBeCalled();
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
        });

        it('should not use amFinishUrl when retpath specified', () => {
            const dispatch = jest.fn();
            const state = {
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    csrf: 'csrf',
                    retpath: '/notAmAtAll'
                },
                auth: {
                    form: {
                        isForceOTP: false
                    },
                    processedAccount: {
                        allowed_auth_methods: ['password'],
                        preferred_auth_method: 'password'
                    }
                },
                social: {
                    providers: [{id: 1, data: {code: 'vk'}}]
                },
                am: {
                    isAm: true,
                    finishOkUrl: '/amFinishOk'
                }
            };
            const getState = jest.fn(() => state);

            const password = 'password';

            multiStepAuthCommitPassword(password)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_password', {
                track_id: 'track',
                csrf_token: 'csrf',
                password,
                retpath: '/notAmAtAll'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(true);
            expect(metrics.goal).toBeCalled();
            expect(metrics.goal).toBeCalledWith(SUCCESS_AUTH_GOAL);
            expect(metrics.send).toBeCalled();
            expect(metrics.send.mock.calls[0][0][1]).toBe(SEND_AUTH_FORM);
            expect(metrics.send.mock.calls[0][0][2]).toBe(SEND_AUTH_FORM_SUCCESS);
            expect(updatePasswordValue).not.toBeCalled();
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
        });

        it('should handle failed response without response object', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn();
                        return this;
                    };

                    this.fail = function() {
                        return this;
                    };
                };

                return new FakeApi();
            });
            const dispatch = jest.fn();
            const state = {
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    retpath: 'retpath',
                    csrf: 'csrf'
                },
                auth: {
                    form: {
                        isForceOTP: false
                    },
                    processedAccount: {
                        allowed_auth_methods: ['password'],
                        preferred_auth_method: 'password'
                    }
                },
                social: {
                    providers: [{id: 1, data: {code: 'vk'}}]
                }
            };
            const getState = jest.fn(() => state);
            const password = 'password';

            multiStepAuthCommitPassword(password)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_password', {
                track_id: 'track',
                csrf_token: 'csrf',
                password,
                retpath: 'retpath'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(metrics.goal).not.toBeCalled();
            expect(metrics.send).not.toBeCalled();
            expect(updatePasswordValue).not.toBeCalled();
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
        });

        it('should handle response with state and redirect url', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({state: 'state', redirect_url: 'redirect_url'});
                        return this;
                    };

                    this.fail = function() {
                        return this;
                    };
                };

                return new FakeApi();
            });
            const dispatch = jest.fn();
            const state = {
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    retpath: 'retpath',
                    csrf: 'csrf'
                },
                auth: {
                    form: {
                        isForceOTP: false
                    },
                    processedAccount: {
                        allowed_auth_methods: ['password'],
                        preferred_auth_method: 'password'
                    }
                },
                social: {
                    providers: [{id: 1, data: {code: 'vk'}}]
                }
            };
            const getState = jest.fn(() => state);
            const password = 'password';

            multiStepAuthCommitPassword(password)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_password', {
                track_id: 'track',
                csrf_token: 'csrf',
                password,
                retpath: 'retpath'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(true);
            expect(metrics.goal).toBeCalled();
            expect(metrics.goal).toBeCalledWith(SUCCESS_AUTH_GOAL);
            expect(metrics.send).toBeCalled();
            expect(metrics.send.mock.calls[0][0][1]).toBe(SEND_AUTH_FORM);
            expect(metrics.send.mock.calls[0][0][2]).toBe(SEND_AUTH_FORM_SUCCESS);
            expect(updatePasswordValue).not.toBeCalled();
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
        });

        it('should handle response with state and without redirect url', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({state: 'state'});
                        return this;
                    };

                    this.fail = function() {
                        return this;
                    };
                };

                return new FakeApi();
            });
            const dispatch = jest.fn();
            const state = {
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    retpath: 'retpath',
                    csrf: 'csrf'
                },
                auth: {
                    form: {
                        isForceOTP: false
                    },
                    processedAccount: {
                        allowed_auth_methods: ['password'],
                        preferred_auth_method: 'password'
                    }
                },
                social: {
                    providers: [{id: 1, data: {code: 'vk'}}]
                }
            };
            const getState = jest.fn(() => state);
            const password = 'password';

            multiStepAuthCommitPassword(password)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_password', {
                track_id: 'track',
                csrf_token: 'csrf',
                password,
                retpath: 'retpath'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(true);
            expect(metrics.goal).toBeCalled();
            expect(metrics.goal).toBeCalledWith(SUCCESS_AUTH_GOAL);
            expect(metrics.send).toBeCalled();
            expect(metrics.send.mock.calls[0][0][1]).toBe(SEND_AUTH_FORM);
            expect(metrics.send.mock.calls[0][0][2]).toBe(SEND_AUTH_FORM_SUCCESS);
            expect(updatePasswordValue).not.toBeCalled();
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
        });

        it('should send login+password to nativeAm', () => {
            api.request.mockImplementation((method) => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        let fnResult = {};

                        if (method === 'auth/accounts') {
                            fnResult = {
                                csrf: 'csrf',
                                accounts: {
                                    processedAccount: {
                                        avatarId: 'processedAccount.avatarId'
                                    }
                                }
                            };
                        } else if (method === 'auth/multi_step/commit_password') {
                            fnResult = {avatarId: null, status: 'ok'};
                        }

                        fn(fnResult);
                        return this;
                    };

                    this.fail = function() {
                        return this;
                    };
                };

                return new FakeApi();
            });

            const login = 'admin';
            const state = {
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    retpath: 'retpath',
                    csrf: 'csrf'
                },
                auth: {
                    form: {
                        isForceOTP: false
                    },
                    processedAccount: {
                        allowed_auth_methods: ['password'],
                        preferred_auth_method: 'password',
                        login,
                        displayLogin: login,
                        avatarId: '123'
                    }
                },
                social: {
                    providers: [{id: 1, data: {code: 'vk'}}]
                },
                settings: {
                    avatar: {
                        avatar_300: 'http://test.com/%avatar_id%'
                    }
                },
                am: {
                    isAm: true
                }
            };
            const getState = jest.fn(() => state);
            const dispatch = jest.fn((action) => {
                if (typeof action === 'function') {
                    action(dispatch, getState);
                }
            });

            const password = 'password';

            multiStepAuthCommitPassword(password)(dispatch, getState);

            expect(dispatch).lastCalledWith(
                expect.objectContaining({
                    type: NATIVE_MOBILE_API_OUTGOING_ACTIONS.AUTH_SUCCEED,
                    payload: {
                        login,
                        password,
                        avatarUrl: 'http://test.com/processedAccount.avatarId',
                        successCb: expect.any(Function)
                    }
                })
            );
        });
    });

    describe('fail cases', () => {
        beforeEach(() => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function() {
                        return this;
                    };

                    this.fail = function(fn) {
                        fn({errors: ['error.1', 'error.2']});
                        return this;
                    };
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            api.request.mockClear();
            domikIsLoading.mockClear();
            setPasswordError.mockClear();
            changeCaptchaState.mockClear();
            updatePasswordValue.mockClear();
            reloadCaptcha.mockClear();
            metrics.send.mockClear();
            metrics.goal.mockClear();
            additionalDataAsk.mockClear();
            changeNativeInputValue.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const state = {
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    retpath: 'retpath',
                    csrf: 'csrf'
                },
                auth: {
                    isCaptchaRequired: false,
                    form: {
                        isForceOTP: false
                    },
                    processedAccount: {
                        allowed_auth_methods: ['password'],
                        preferred_auth_method: 'password'
                    }
                },
                social: {
                    providers: [{id: 1, data: {code: 'vk'}}]
                }
            };
            const getState = jest.fn(() => state);
            const password = 'password';

            multiStepAuthCommitPassword(password)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_password', {
                track_id: 'track',
                csrf_token: 'csrf',
                password,
                retpath: 'retpath'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(setPasswordError).toBeCalled();
            expect(setPasswordError.mock.calls[0][0]).toBe('error.1');
            expect(metrics.send).toBeCalled();
            expect(metrics.send.mock.calls[0][0][1]).toBe(SEND_AUTH_FORM);
            expect(metrics.send.mock.calls[0][0][2]).toBe(SEND_AUTH_FORM_ERROR);
            expect(updatePasswordValue).not.toBeCalled();
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
        });

        it('should handle captcha required error', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function() {
                        return this;
                    };

                    this.fail = function(fn) {
                        fn({errors: ['captcha.required', 'error.2']});
                        return this;
                    };
                };

                return new FakeApi();
            });
            const dispatch = jest.fn();
            const state = {
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    retpath: 'retpath',
                    csrf: 'csrf'
                },
                auth: {
                    isCaptchaRequired: true,
                    form: {
                        isForceOTP: false
                    },
                    processedAccount: {
                        allowed_auth_methods: ['password'],
                        preferred_auth_method: 'password'
                    }
                },
                social: {
                    providers: [{id: 1, data: {code: 'vk'}}]
                }
            };
            const getState = jest.fn(() => state);
            const password = 'password';

            multiStepAuthCommitPassword(password)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_password', {
                track_id: 'track',
                csrf_token: 'csrf',
                password,
                retpath: 'retpath'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(setPasswordError).toBeCalled();
            expect(setPasswordError.mock.calls[0][0]).toBe('captcha.required');
            expect(metrics.send).toBeCalled();
            expect(metrics.send.mock.calls[0][0][1]).toBe(SEND_AUTH_FORM);
            expect(metrics.send.mock.calls[0][0][2]).toBe(SEND_AUTH_FORM_ERROR);
            expect(changeCaptchaState).toBeCalled();
            expect(changeCaptchaState).toBeCalledWith(true);
            expect(reloadCaptcha).toBeCalled();
            expect(updatePasswordValue).not.toBeCalled();
        });

        it('should handle captcha required error without reload captcha', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function() {
                        return this;
                    };

                    this.fail = function(fn) {
                        fn({errors: ['captcha.required', 'error.2']});
                        return this;
                    };
                };

                return new FakeApi();
            });
            const dispatch = jest.fn();
            const state = {
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    retpath: 'retpath',
                    csrf: 'csrf'
                },
                auth: {
                    isCaptchaRequired: true,
                    form: {
                        isForceOTP: false
                    },
                    processedAccount: {
                        allowed_auth_methods: ['password'],
                        preferred_auth_method: 'password'
                    }
                },
                social: {
                    providers: [{id: 1, data: {code: 'vk'}}]
                }
            };
            const getState = jest.fn(() => state);
            const password = 'password';

            multiStepAuthCommitPassword(password)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_password', {
                track_id: 'track',
                csrf_token: 'csrf',
                password,
                retpath: 'retpath'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(setPasswordError).toBeCalled();
            expect(setPasswordError.mock.calls[0][0]).toBe('captcha.required');
            expect(metrics.send).toBeCalled();
            expect(metrics.send.mock.calls[0][0][1]).toBe(SEND_AUTH_FORM);
            expect(metrics.send.mock.calls[0][0][2]).toBe(SEND_AUTH_FORM_ERROR);
            expect(changeCaptchaState).toBeCalled();
            expect(changeCaptchaState).toBeCalledWith(true);
            expect(updatePasswordValue).not.toBeCalled();
        });

        it('should handle captcha password.not_matched error', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function() {
                        return this;
                    };

                    this.fail = function(fn) {
                        fn({errors: ['password.not_matched', 'error.2']});
                        return this;
                    };
                };

                return new FakeApi();
            });
            const dispatch = jest.fn();
            const state = {
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    retpath: 'retpath',
                    csrf: 'csrf'
                },
                auth: {
                    isCaptchaRequired: false,
                    form: {
                        isForceOTP: false
                    },
                    processedAccount: {
                        allowed_auth_methods: ['password'],
                        preferred_auth_method: 'password'
                    }
                },
                social: {
                    providers: [{id: 1, data: {code: 'vk'}}]
                }
            };
            const getState = jest.fn(() => state);
            const password = 'password';

            multiStepAuthCommitPassword(password)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_password', {
                track_id: 'track',
                csrf_token: 'csrf',
                password,
                retpath: 'retpath'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(setPasswordError).toBeCalled();
            expect(setPasswordError.mock.calls[0][0]).toBe('password.not_matched');
            expect(metrics.send).toBeCalled();
            expect(metrics.send.mock.calls[0][0][1]).toBe(SEND_AUTH_FORM);
            expect(metrics.send.mock.calls[0][0][2]).toBe(SEND_AUTH_FORM_ERROR);
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
            expect(updatePasswordValue).toBeCalled();
            expect(updatePasswordValue).toBeCalledWith('');
        });

        it('should handle captcha password.empty error', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function() {
                        return this;
                    };

                    this.fail = function(fn) {
                        fn({errors: ['password.empty', 'error.2']});
                        return this;
                    };
                };

                return new FakeApi();
            });
            const dispatch = jest.fn();
            const state = {
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    retpath: 'retpath',
                    csrf: 'csrf'
                },
                auth: {
                    isCaptchaRequired: true,
                    form: {
                        isForceOTP: false
                    },
                    processedAccount: {
                        allowed_auth_methods: ['password'],
                        preferred_auth_method: 'password'
                    }
                },
                social: {
                    providers: [{id: 1, data: {code: 'vk'}}]
                }
            };
            const getState = jest.fn(() => state);
            const password = 'password';

            multiStepAuthCommitPassword(password)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_password', {
                track_id: 'track',
                csrf_token: 'csrf',
                password,
                retpath: 'retpath'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(setPasswordError).toBeCalled();
            expect(setPasswordError.mock.calls[0][0]).toBe('password.empty');
            expect(metrics.send).toBeCalled();
            expect(metrics.send.mock.calls[0][0][1]).toBe(SEND_AUTH_FORM);
            expect(metrics.send.mock.calls[0][0][2]).toBe(SEND_AUTH_FORM_ERROR);
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
            expect(updatePasswordValue).toBeCalled();
            expect(updatePasswordValue).toBeCalledWith('');
        });

        it('should handle captcha rfc_otp.invalid error', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function() {
                        return this;
                    };

                    this.fail = function(fn) {
                        fn({errors: ['rfc_otp.invalid', 'error.2']});
                        return this;
                    };
                };

                return new FakeApi();
            });
            const dispatch = jest.fn();
            const state = {
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    retpath: 'retpath',
                    csrf: 'csrf'
                },
                auth: {
                    isCaptchaRequired: true,
                    form: {
                        isForceOTP: false
                    },
                    processedAccount: {
                        allowed_auth_methods: ['password'],
                        preferred_auth_method: 'password'
                    }
                },
                social: {
                    providers: [{id: 1, data: {code: 'vk'}}]
                }
            };
            const getState = jest.fn(() => state);
            const password = 'password';

            multiStepAuthCommitPassword(password)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_password', {
                track_id: 'track',
                csrf_token: 'csrf',
                password,
                retpath: 'retpath'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(setPasswordError).toBeCalled();
            expect(setPasswordError.mock.calls[0][0]).toBe('rfc_otp.invalid');
            expect(metrics.send).toBeCalled();
            expect(metrics.send.mock.calls[0][0][1]).toBe(SEND_AUTH_FORM);
            expect(metrics.send.mock.calls[0][0][2]).toBe(SEND_AUTH_FORM_ERROR);
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
            expect(updatePasswordValue).toBeCalled();
            expect(updatePasswordValue).toBeCalledWith('');
        });

        it('should not send login+password to nativeAm', () => {
            const dispatch = jest.fn();
            const login = 'admin';
            const state = {
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    retpath: 'retpath',
                    csrf: 'csrf'
                },
                auth: {
                    form: {
                        isForceOTP: false
                    },
                    processedAccount: {
                        allowed_auth_methods: ['sms_code'],
                        preferred_auth_method: 'sms_code',
                        login
                    }
                },
                social: {
                    providers: [{id: 1, data: {code: 'vk'}}]
                },
                am: {
                    isAm: true
                }
            };
            const getState = jest.fn(() => state);

            const password = 'password';

            multiStepAuthCommitPassword(password)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_password', {
                track_id: 'track',
                csrf_token: 'csrf',
                password,
                retpath: 'retpath'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(4);
            expect(dispatch).not.toBeCalledWith({
                type: NATIVE_MOBILE_API_OUTGOING_ACTIONS.AUTH_SUCCEED,
                payload: {
                    login,
                    password
                }
            });
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading).toBeCalledWith(true);
        });

        it('should not send login+password to nativeAm if login is phone', () => {
            const dispatch = jest.fn();
            const login = 'admin';
            const state = {
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    retpath: 'retpath',
                    csrf: 'csrf'
                },
                auth: {
                    form: {
                        isForceOTP: false
                    },
                    processedAccount: {
                        allowed_auth_methods: ['password'],
                        preferred_auth_method: 'password',
                        login
                    }
                },
                social: {
                    providers: [{id: 1, data: {code: 'vk'}}]
                },
                am: {
                    isAm: true
                }
            };
            const getState = jest.fn(() => state);

            const password = 'password';

            multiStepAuthCommitPassword(password)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_password', {
                track_id: 'track',
                csrf_token: 'csrf',
                password,
                retpath: 'retpath'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(4);
            expect(dispatch).not.toBeCalledWith({
                type: NATIVE_MOBILE_API_OUTGOING_ACTIONS.AUTH_SUCCEED,
                payload: {
                    login,
                    password
                }
            });
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading).toBeCalledWith(true);
        });
    });
});
