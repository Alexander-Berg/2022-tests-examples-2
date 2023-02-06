jest.mock('../../../api', () => ({
    request: jest.fn()
}));

import multiStepAuthStart from '../multiStepAuthStart';
import * as api from '../../../api';
import {
    changeProcessedAccount,
    updateTokensSuccess,
    domikIsLoading,
    canRegister,
    setupBackPane,
    setLoginError,
    updateLoginValue,
    setLoginAbleToRestore
} from '../';
import switchToModeWelcome from '../switchToModeWelcome';
import switchToModeMagic from '../switchToModeMagic';
import switchToModeAddingAccount from '../switchToModeAddingAccount';
import {
    SHOW_LOGIN_FORM,
    SEND_LOGIN_FORM,
    SEND_LOGIN_FORM_SUCCESS,
    SEND_LOGIN_FORM_ERROR,
    SEND_LOGIN_FORM_CAN_REGISTER
} from '../../metrics_constants';
import metrics from '../../../metrics';

jest.mock('../', () => ({
    changeProcessedAccount: jest.fn(),
    updateTokensSuccess: jest.fn(),
    domikIsLoading: jest.fn(),
    canRegister: jest.fn(),
    setupBackPane: jest.fn(),
    setLoginError: jest.fn(),
    updateLoginValue: jest.fn(),
    updateAuthMailStatus: jest.fn(),
    setLoginAbleToRestore: jest.fn()
}));
jest.mock('../switchToModeWelcome');
jest.mock('../switchToModeMagic');
jest.mock('../switchToModeAddingAccount');
jest.mock('../../../metrics', () => ({
    send: jest.fn()
}));

describe('Actions: multiStepAuthStart', () => {
    describe('success cases', () => {
        beforeEach(() => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({
                            auth_methods: [],
                            preferred_auth_method: '',
                            track_id: 'track',
                            csrf_token: 'magic_csrf',
                            magic_link_email: 'email'
                        });
                        return this;
                    };

                    this.fail = function() {
                        return this;
                    };

                    this.always = function(fn) {
                        fn();
                        return this;
                    };
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            api.request.mockClear();
            changeProcessedAccount.mockClear();
            updateTokensSuccess.mockClear();
            domikIsLoading.mockClear();
            canRegister.mockClear();
            setupBackPane.mockClear();
            setLoginError.mockClear();
            updateLoginValue.mockClear();
            switchToModeWelcome.mockClear();
            switchToModeMagic.mockClear();
            switchToModeAddingAccount.mockClear();
            setLoginAbleToRestore.mockClear();
            metrics.send.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    neoPhonish: {origins: ['neophonish']}
                },
                auth: {
                    process_uuid: 'process_uuid',
                    unitedAccounts: {},
                    form: {
                        isForceOTP: false
                    }
                },
                mailAuth: {},
                settings: {}
            }));

            const login = 'login';
            const backPane = 'backPane';

            multiStepAuthStart({login, backPane})(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/start', {
                csrf_token: 'csrf',
                login,
                process_uuid: 'process_uuid'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(updateLoginValue).toBeCalled();
            expect(updateLoginValue).toBeCalledWith(login);
            expect(canRegister).toBeCalled();
            expect(canRegister).toBeCalledWith({isCanRegister: false});
            expect(metrics.send).toBeCalled();
            expect(metrics.send).toBeCalledWith([SHOW_LOGIN_FORM, SEND_LOGIN_FORM, SEND_LOGIN_FORM_SUCCESS]);
            expect(setupBackPane).toBeCalled();
            expect(setupBackPane).toBeCalledWith(backPane);
            expect(changeProcessedAccount).toBeCalled();
            expect(changeProcessedAccount).toBeCalledWith({
                isAddedAccount: true,
                allowed_auth_methods: [],
                preferred_auth_method: 'password',
                avatarId: '0/0-0',
                email: 'email',
                login
            });
            expect(updateTokensSuccess).toBeCalled();
            expect(updateTokensSuccess).toBeCalledWith('track', 'magic_csrf');
            expect(switchToModeWelcome).toBeCalled();
            expect(switchToModeAddingAccount).not.toBeCalled();
            expect(switchToModeMagic).not.toBeCalled();
        });

        it('should send api request with valid params and without process_uuid', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    neoPhonish: {origins: ['neophonish']}
                },
                auth: {
                    unitedAccounts: {},
                    form: {
                        isForceOTP: false
                    }
                },
                mailAuth: {},
                settings: {}
            }));

            const login = 'login';
            const backPane = 'backPane';

            multiStepAuthStart({login, backPane})(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/start', {
                csrf_token: 'csrf',
                login
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(updateLoginValue).toBeCalled();
            expect(updateLoginValue).toBeCalledWith(login);
            expect(canRegister).toBeCalled();
            expect(canRegister).toBeCalledWith({isCanRegister: false});
            expect(metrics.send).toBeCalled();
            expect(metrics.send).toBeCalledWith([SHOW_LOGIN_FORM, SEND_LOGIN_FORM, SEND_LOGIN_FORM_SUCCESS]);
            expect(setupBackPane).toBeCalled();
            expect(setupBackPane).toBeCalledWith(backPane);
            expect(changeProcessedAccount).toBeCalled();
            expect(changeProcessedAccount).toBeCalledWith({
                isAddedAccount: true,
                allowed_auth_methods: [],
                preferred_auth_method: 'password',
                avatarId: '0/0-0',
                email: 'email',
                login
            });
            expect(updateTokensSuccess).toBeCalled();
            expect(updateTokensSuccess).toBeCalledWith('track', 'magic_csrf');
            expect(switchToModeWelcome).toBeCalled();
            expect(switchToModeAddingAccount).not.toBeCalled();
            expect(switchToModeMagic).not.toBeCalled();
        });

        it('should send api request with valid params and empty backpane', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    neoPhonish: {origins: ['neophonish']}
                },
                auth: {
                    process_uuid: 'process_uuid',
                    unitedAccounts: {},
                    form: {
                        isForceOTP: false
                    }
                },
                mailAuth: {},
                settings: {}
            }));

            const login = 'login';

            multiStepAuthStart({login})(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/start', {
                csrf_token: 'csrf',
                login,
                process_uuid: 'process_uuid'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(updateLoginValue).toBeCalled();
            expect(updateLoginValue).toBeCalledWith(login);
            expect(canRegister).toBeCalled();
            expect(canRegister).toBeCalledWith({isCanRegister: false});
            expect(metrics.send).toBeCalled();
            expect(metrics.send).toBeCalledWith([SHOW_LOGIN_FORM, SEND_LOGIN_FORM, SEND_LOGIN_FORM_SUCCESS]);
            expect(setupBackPane).not.toBeCalled();
            expect(changeProcessedAccount).toBeCalled();
            expect(changeProcessedAccount).toBeCalledWith({
                isAddedAccount: true,
                allowed_auth_methods: [],
                preferred_auth_method: 'password',
                avatarId: '0/0-0',
                email: 'email',
                login
            });
            expect(updateTokensSuccess).toBeCalled();
            expect(updateTokensSuccess).toBeCalledWith('track', 'magic_csrf');
            expect(switchToModeWelcome).toBeCalled();
            expect(switchToModeAddingAccount).not.toBeCalled();
            expect(switchToModeMagic).not.toBeCalled();
        });

        it('should handle can register response', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({
                            can_register: true
                        });
                        return this;
                    };

                    this.fail = function() {
                        return this;
                    };

                    this.always = function(fn) {
                        fn();
                        return this;
                    };
                };

                return new FakeApi();
            });
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    neoPhonish: {origins: ['neophonish']}
                },
                auth: {
                    process_uuid: 'process_uuid',
                    unitedAccounts: {},
                    form: {
                        isForceOTP: false
                    },
                    mode: ''
                },
                mailAuth: {},
                settings: {}
            }));

            const login = 'login';
            const backPane = 'backPane';

            multiStepAuthStart({login, backPane})(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/start', {
                csrf_token: 'csrf',
                login,
                process_uuid: 'process_uuid'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(domikIsLoading.mock.calls[2][0]).toBe(false);
            expect(setLoginError).toBeCalled();
            expect(setLoginError.mock.calls.length).toBe(1);
            expect(setLoginError.mock.calls[0][0]).toBe('login.can_register');
            expect(updateLoginValue).toBeCalled();
            expect(updateLoginValue).toBeCalledWith(login);
            expect(canRegister).toBeCalled();
            expect(canRegister).toBeCalledWith({
                isCanRegister: true,
                registrationLogin: login,
                registrationType: 'portal',
                registrationPhoneNumber: '',
                registrationCountry: ''
            });
            expect(metrics.send).toBeCalledWith([SHOW_LOGIN_FORM, SEND_LOGIN_FORM, SEND_LOGIN_FORM_CAN_REGISTER]);
            expect(setupBackPane).not.toBeCalled();
            expect(changeProcessedAccount).not.toBeCalled();
            expect(updateTokensSuccess).not.toBeCalled();
            expect(switchToModeWelcome).not.toBeCalled();
            expect(switchToModeAddingAccount).not.toBeCalled();
            expect(switchToModeMagic).not.toBeCalled();
        });

        it('should handle can register and additional info response', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({
                            can_register: true,
                            login: 'response_login',
                            account_type: 'account_type',
                            phone_number: {
                                original: 'phone_number'
                            },
                            country: 'country'
                        });
                        return this;
                    };

                    this.fail = function() {
                        return this;
                    };

                    this.always = function(fn) {
                        fn();
                        return this;
                    };
                };

                return new FakeApi();
            });
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    neoPhonish: {origins: ['neophonish']}
                },
                auth: {
                    process_uuid: 'process_uuid',
                    unitedAccounts: {},
                    form: {
                        isForceOTP: false
                    },
                    mode: ''
                },
                mailAuth: {},
                settings: {}
            }));

            const login = 'login';
            const backPane = 'backPane';

            multiStepAuthStart({login, backPane})(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/start', {
                csrf_token: 'csrf',
                login,
                process_uuid: 'process_uuid'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(domikIsLoading.mock.calls[2][0]).toBe(false);
            expect(setLoginError).toBeCalled();
            expect(setLoginError.mock.calls.length).toBe(1);
            expect(setLoginError.mock.calls[0][0]).toBe('login.can_register');
            expect(updateLoginValue).toBeCalled();
            expect(updateLoginValue).toBeCalledWith(login);
            expect(canRegister).toBeCalled();
            expect(canRegister).toBeCalledWith({
                isCanRegister: true,
                registrationLogin: 'response_login',
                registrationType: 'account_type',
                registrationPhoneNumber: 'phone_number',
                registrationCountry: 'country'
            });
            expect(metrics.send).toBeCalledWith([SHOW_LOGIN_FORM, SEND_LOGIN_FORM, SEND_LOGIN_FORM_CAN_REGISTER]);
            expect(setupBackPane).not.toBeCalled();
            expect(changeProcessedAccount).not.toBeCalled();
            expect(updateTokensSuccess).not.toBeCalled();
            expect(switchToModeWelcome).not.toBeCalled();
            expect(switchToModeAddingAccount).not.toBeCalled();
            expect(switchToModeMagic).not.toBeCalled();
        });

        it('should handle can register response and switch to add account page for magic mode', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({
                            can_register: true
                        });
                        return this;
                    };

                    this.fail = function() {
                        return this;
                    };

                    this.always = function(fn) {
                        fn();
                        return this;
                    };
                };

                return new FakeApi();
            });
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    neoPhonish: {origins: ['neophonish']}
                },
                auth: {
                    process_uuid: 'process_uuid',
                    unitedAccounts: {},
                    form: {
                        isForceOTP: false
                    },
                    mode: 'magic'
                },
                mailAuth: {},
                settings: {}
            }));

            const login = 'login';
            const backPane = 'backPane';

            multiStepAuthStart({login, backPane})(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/start', {
                csrf_token: 'csrf',
                login,
                process_uuid: 'process_uuid'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(3);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(domikIsLoading.mock.calls[2][0]).toBe(false);
            expect(setLoginError).toBeCalled();
            expect(setLoginError.mock.calls.length).toBe(1);
            expect(setLoginError.mock.calls[0][0]).toBe('login.can_register');
            expect(updateLoginValue).toBeCalled();
            expect(updateLoginValue).toBeCalledWith(login);
            expect(canRegister).toBeCalled();
            expect(canRegister).toBeCalledWith({
                isCanRegister: true,
                registrationLogin: login,
                registrationType: 'portal',
                registrationPhoneNumber: '',
                registrationCountry: ''
            });
            expect(metrics.send).toBeCalledWith([SHOW_LOGIN_FORM, SEND_LOGIN_FORM, SEND_LOGIN_FORM_CAN_REGISTER]);
            expect(setupBackPane).not.toBeCalled();
            expect(changeProcessedAccount).not.toBeCalled();
            expect(updateTokensSuccess).not.toBeCalled();
            expect(switchToModeWelcome).not.toBeCalled();
            expect(switchToModeAddingAccount).toBeCalled();
            expect(switchToModeMagic).not.toBeCalled();
        });

        it('should handle existing processed account', () => {
            const dispatch = jest.fn();
            const processedAccount = {
                login: 'login',
                avatarId: '1/1-1'
            };
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    neoPhonish: {origins: ['neophonish']}
                },
                auth: {
                    process_uuid: 'process_uuid',
                    unitedAccounts: {
                        1: processedAccount
                    },
                    form: {
                        isForceOTP: false
                    }
                },
                mailAuth: {},
                settings: {}
            }));

            const login = processedAccount.login;
            const backPane = 'backPane';

            multiStepAuthStart({login, backPane})(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/start', {
                csrf_token: 'csrf',
                login,
                process_uuid: 'process_uuid'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(updateLoginValue).toBeCalled();
            expect(updateLoginValue).toBeCalledWith(login);
            expect(canRegister).toBeCalled();
            expect(canRegister).toBeCalledWith({isCanRegister: false});
            expect(metrics.send).toBeCalled();
            expect(metrics.send).toBeCalledWith([SHOW_LOGIN_FORM, SEND_LOGIN_FORM, SEND_LOGIN_FORM_SUCCESS]);
            expect(setupBackPane).toBeCalled();
            expect(setupBackPane).toBeCalledWith(backPane);
            expect(changeProcessedAccount).toBeCalled();
            expect(changeProcessedAccount).toBeCalledWith({
                allowed_auth_methods: [],
                preferred_auth_method: 'password',
                avatarId: processedAccount.avatarId,
                email: 'email',
                login: processedAccount.login
            });
            expect(updateTokensSuccess).toBeCalled();
            expect(updateTokensSuccess).toBeCalledWith('track', 'magic_csrf');
            expect(switchToModeWelcome).toBeCalled();
            expect(switchToModeAddingAccount).not.toBeCalled();
            expect(switchToModeMagic).not.toBeCalled();
        });

        it('should handle existing processed account with fallbacks data', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({
                            track_id: 'track',
                            csrf_token: 'magic_csrf',
                            magic_link_email: 'email'
                        });
                        return this;
                    };

                    this.fail = function() {
                        return this;
                    };

                    this.always = function(fn) {
                        fn();
                        return this;
                    };
                };

                return new FakeApi();
            });
            const dispatch = jest.fn();
            const processedAccount = {
                login: 'login',
                avatarId: '1/1-1'
            };
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    neoPhonish: {origins: ['neophonish']}
                },
                auth: {
                    process_uuid: 'process_uuid',
                    unitedAccounts: {
                        1: processedAccount
                    },
                    form: {
                        isForceOTP: false
                    }
                },
                mailAuth: {},
                settings: {}
            }));

            const login = processedAccount.login;
            const backPane = 'backPane';

            multiStepAuthStart({login, backPane})(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/start', {
                csrf_token: 'csrf',
                login,
                process_uuid: 'process_uuid'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(updateLoginValue).toBeCalled();
            expect(updateLoginValue).toBeCalledWith(login);
            expect(canRegister).toBeCalled();
            expect(canRegister).toBeCalledWith({isCanRegister: false});
            expect(metrics.send).toBeCalled();
            expect(metrics.send).toBeCalledWith([SHOW_LOGIN_FORM, SEND_LOGIN_FORM, SEND_LOGIN_FORM_SUCCESS]);
            expect(setupBackPane).toBeCalled();
            expect(setupBackPane).toBeCalledWith(backPane);
            expect(changeProcessedAccount).toBeCalled();
            expect(changeProcessedAccount).toBeCalledWith({
                allowed_auth_methods: [],
                preferred_auth_method: 'password',
                avatarId: processedAccount.avatarId,
                email: 'email',
                login: processedAccount.login
            });
            expect(updateTokensSuccess).toBeCalled();
            expect(updateTokensSuccess).toBeCalledWith('track', 'magic_csrf');
            expect(switchToModeWelcome).toBeCalled();
            expect(switchToModeAddingAccount).not.toBeCalled();
            expect(switchToModeMagic).not.toBeCalled();
        });

        it('should handle existing processed account with additional data', () => {
            const dispatch = jest.fn();
            const processedAccount = {
                login: 'login',
                avatarId: '1/1-1',
                allowed_auth_methods: ['otp', 'password'],
                preferred_auth_method: ['otp']
            };
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    neoPhonish: {origins: ['neophonish']}
                },
                auth: {
                    process_uuid: 'process_uuid',
                    unitedAccounts: {
                        1: processedAccount
                    },
                    form: {
                        isForceOTP: false
                    }
                },
                mailAuth: {},
                settings: {}
            }));

            const login = processedAccount.login;
            const backPane = 'backPane';

            multiStepAuthStart({login, backPane})(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/start', {
                csrf_token: 'csrf',
                login,
                process_uuid: 'process_uuid'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(updateLoginValue).toBeCalled();
            expect(updateLoginValue).toBeCalledWith(login);
            expect(canRegister).toBeCalled();
            expect(canRegister).toBeCalledWith({isCanRegister: false});
            expect(metrics.send).toBeCalled();
            expect(metrics.send).toBeCalledWith([SHOW_LOGIN_FORM, SEND_LOGIN_FORM, SEND_LOGIN_FORM_SUCCESS]);
            expect(setupBackPane).toBeCalled();
            expect(setupBackPane).toBeCalledWith(backPane);
            expect(changeProcessedAccount).toBeCalled();
            expect(changeProcessedAccount).toBeCalledWith({
                allowed_auth_methods: ['otp', 'password'],
                preferred_auth_method: processedAccount.preferred_auth_method,
                avatarId: processedAccount.avatarId,
                email: 'email',
                login: processedAccount.login
            });
            expect(updateTokensSuccess).toBeCalled();
            expect(updateTokensSuccess).toBeCalledWith('track', 'magic_csrf');
            expect(switchToModeWelcome).toBeCalled();
            expect(switchToModeAddingAccount).not.toBeCalled();
            expect(switchToModeMagic).not.toBeCalled();
        });

        it('should handle existing processed account with additional data', () => {
            const dispatch = jest.fn();
            const processedAccount = {
                login: 'login',
                avatarId: '1/1-1',
                allowed_auth_methods: ['magic', 'password'],
                preferred_auth_method: 'magic'
            };
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    neoPhonish: {origins: ['neophonish']}
                },
                auth: {
                    process_uuid: 'process_uuid',
                    unitedAccounts: {
                        1: processedAccount
                    },
                    form: {
                        isForceOTP: false
                    }
                },
                mailAuth: {},
                settings: {}
            }));

            const login = processedAccount.login;
            const backPane = 'backPane';

            multiStepAuthStart({login, backPane})(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/start', {
                csrf_token: 'csrf',
                login,
                process_uuid: 'process_uuid'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(updateLoginValue).toBeCalled();
            expect(updateLoginValue).toBeCalledWith(login);
            expect(canRegister).toBeCalled();
            expect(canRegister).toBeCalledWith({isCanRegister: false});
            expect(metrics.send).toBeCalled();
            expect(metrics.send).toBeCalledWith([SHOW_LOGIN_FORM, SEND_LOGIN_FORM, SEND_LOGIN_FORM_SUCCESS]);
            expect(setupBackPane).toBeCalled();
            expect(setupBackPane).toBeCalledWith(backPane);
            expect(changeProcessedAccount).toBeCalled();
            expect(changeProcessedAccount).toBeCalledWith({
                allowed_auth_methods: ['magic', 'password'],
                preferred_auth_method: processedAccount.preferred_auth_method,
                avatarId: processedAccount.avatarId,
                email: 'email',
                login: processedAccount.login
            });
            expect(updateTokensSuccess).toBeCalled();
            expect(updateTokensSuccess).toBeCalledWith('track', 'magic_csrf');
            expect(switchToModeWelcome).not.toBeCalled();
            expect(switchToModeAddingAccount).not.toBeCalled();
            expect(switchToModeMagic).toBeCalled();
        });

        it('should show otp field with preferred magic method', () => {
            const dispatch = jest.fn();
            const processedAccount = {
                login: 'login',
                avatarId: '1/1-1',
                allowed_auth_methods: ['magic', 'otp'],
                preferred_auth_method: 'magic'
            };
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    neoPhonish: {origins: ['neophonish']}
                },
                auth: {
                    process_uuid: 'process_uuid',
                    unitedAccounts: {
                        1: processedAccount
                    },
                    form: {
                        isForceOTP: false
                    }
                },
                mailAuth: {},
                settings: {
                    ua: {
                        isTouch: true
                    }
                }
            }));

            const login = processedAccount.login;
            const backPane = 'backPane';

            multiStepAuthStart({login, backPane})(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/start', {
                csrf_token: 'csrf',
                login,
                process_uuid: 'process_uuid'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(updateLoginValue).toBeCalled();
            expect(updateLoginValue).toBeCalledWith(login);
            expect(canRegister).toBeCalled();
            expect(canRegister).toBeCalledWith({isCanRegister: false});
            expect(metrics.send).toBeCalled();
            expect(metrics.send).toBeCalledWith([SHOW_LOGIN_FORM, SEND_LOGIN_FORM, SEND_LOGIN_FORM_SUCCESS]);
            expect(setupBackPane).toBeCalled();
            expect(setupBackPane).toBeCalledWith(backPane);
            expect(changeProcessedAccount).toBeCalled();
            expect(changeProcessedAccount).toBeCalledWith({
                allowed_auth_methods: ['magic', 'otp'],
                preferred_auth_method: processedAccount.preferred_auth_method,
                avatarId: processedAccount.avatarId,
                email: 'email',
                login: processedAccount.login
            });
            expect(updateTokensSuccess).toBeCalled();
            expect(updateTokensSuccess).toBeCalledWith('track', 'magic_csrf');
            expect(switchToModeWelcome).toBeCalled();
            expect(switchToModeAddingAccount).not.toBeCalled();
            expect(switchToModeMagic).not.toBeCalled();
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

                    this.always = function(fn) {
                        fn();
                        return this;
                    };
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            api.request.mockClear();
            changeProcessedAccount.mockClear();
            updateTokensSuccess.mockClear();
            domikIsLoading.mockClear();
            canRegister.mockClear();
            setupBackPane.mockClear();
            setLoginError.mockClear();
            updateLoginValue.mockClear();
            switchToModeWelcome.mockClear();
            switchToModeMagic.mockClear();
            switchToModeAddingAccount.mockClear();
            setLoginAbleToRestore.mockClear();
            metrics.send.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    neoPhonish: {origins: ['neophonish']}
                },
                auth: {
                    process_uuid: 'process_uuid',
                    form: {}
                },
                mailAuth: {},
                settings: {}
            }));

            const login = 'login';
            const backPane = 'backPane';

            multiStepAuthStart({login, backPane})(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/start', {
                csrf_token: 'csrf',
                login,
                process_uuid: 'process_uuid'
            });
            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(setLoginError).toBeCalled();
            expect(setLoginError.mock.calls.length).toBe(1);
            expect(setLoginError.mock.calls[0][0]).toBe('error.1');
            expect(updateLoginValue).toBeCalled();
            expect(updateLoginValue).toBeCalledWith(login);
            expect(canRegister).toBeCalled();
            expect(canRegister).toBeCalledWith({isCanRegister: false});
            expect(metrics.send).toBeCalled();
            expect(metrics.send).toBeCalledWith([SHOW_LOGIN_FORM, SEND_LOGIN_FORM, SEND_LOGIN_FORM_ERROR, 'error.1']);
            expect(setupBackPane).not.toBeCalled();
            expect(changeProcessedAccount).not.toBeCalled();
            expect(updateTokensSuccess).not.toBeCalled();
            expect(switchToModeWelcome).not.toBeCalled();
            expect(switchToModeAddingAccount).toBeCalled();
            expect(switchToModeMagic).not.toBeCalled();
            expect(setLoginAbleToRestore).toBeCalledWith(false);
            expect(setLoginAbleToRestore.mock.calls.length).toBe(1);
        });

        it('should send api request with valid params even if login contains @', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    neoPhonish: {origins: ['neophonish']}
                },
                auth: {
                    process_uuid: 'process_uuid',
                    form: {}
                },
                mailAuth: {},
                settings: {}
            }));

            const login = 'login@okna.ru';
            const backPane = 'backPane';

            multiStepAuthStart({login, backPane})(dispatch, getState);

            expect(api.request).toBeCalledWith('auth/multi_step/start', {
                csrf_token: 'csrf',
                login,
                process_uuid: 'process_uuid'
            });
        });

        it('should send api request with valid params if pdd_domain is defined', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    neoPhonish: {origins: ['neophonish']}
                },
                auth: {
                    process_uuid: 'process_uuid',
                    form: {
                        pdd_domain: 'okna.ru'
                    }
                },
                mailAuth: {},
                settings: {}
            }));

            const login = 'login';
            const backPane = 'backPane';
            const is_pdd = '1';

            multiStepAuthStart({login, backPane})(dispatch, getState);

            expect(api.request).toBeCalledWith('auth/multi_step/start', {
                csrf_token: 'csrf',
                login: 'login@okna.ru',
                is_pdd,
                process_uuid: 'process_uuid'
            });
        });

        it('Должен передать в API верные параметры если авторизация из саджеста социализма', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    neoPhonish: {origins: ['neophonish']}
                },
                auth: {
                    process_uuid: 'process_uuid',
                    form: {}
                },
                mailAuth: {},
                settings: {},
                socialSuggest: {
                    authRetpath: 'socialSuggestAuthRetpath',
                    authTrackId: 'socialSuggestAuthTrackId',
                    processUUID: 'socialSuggestProcessUUID'
                }
            }));

            const login = 'login';
            const backPane = 'backPane';

            multiStepAuthStart({login, backPane, isAuthFromSocialSuggest: true})(dispatch, getState);

            expect(api.request).toBeCalledWith('auth/multi_step/start', {
                csrf_token: 'csrf',
                login: 'login',
                process_uuid: 'socialSuggestProcessUUID',
                social_track_id: 'socialSuggestAuthTrackId'
            });
        });
    });
});
