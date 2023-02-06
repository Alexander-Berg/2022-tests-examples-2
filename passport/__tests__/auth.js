import authReducer from '../auth';

describe('Reducers: auth', () => {
    it('should handle SET_LOGIN_ERROR action', () => {
        const state = {};
        const action = {
            type: 'SET_LOGIN_ERROR',
            error: 'error'
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            loginError: 'error'
        });
    });

    it('should handle SET_PASSWORD_ERROR action', () => {
        const state = {};
        const action = {
            type: 'SET_PASSWORD_ERROR',
            error: 'error'
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            passwordError: 'error'
        });
    });

    it('should handle SET_CAPTCHA_ERROR action', () => {
        const state = {};
        const action = {
            type: 'SET_CAPTCHA_ERROR',
            error: 'error'
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            captchaError: 'error'
        });
    });

    it('should handle SET_MAGIC_ERROR action', () => {
        const state = {};
        const action = {
            type: 'SET_MAGIC_ERROR',
            error: 'error'
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            magicError: 'error'
        });
    });

    it('should handle CAN_REGISTER action', () => {
        const state = {};
        const action = {
            type: 'CAN_REGISTER',
            isCanRegister: true,
            registrationLogin: 'registrationLogin',
            registrationType: 'registrationType',
            registrationPhoneNumber: 'registrationPhoneNumber',
            registrationCountry: 'registrationCountry'
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            form: {
                isCanRegister: true,
                registrationLogin: 'registrationLogin',
                registrationType: 'registrationType',
                registrationPhoneNumber: 'registrationPhoneNumber',
                registrationCountry: 'registrationCountry'
            }
        });
    });

    it('should handle CAN_REGISTER action with fallback', () => {
        const state = {};
        const action = {
            type: 'CAN_REGISTER',
            isCanRegister: true
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            form: {
                isCanRegister: true,
                registrationLogin: '',
                registrationType: '',
                registrationPhoneNumber: '',
                registrationCountry: ''
            }
        });
    });

    it('should handle CHANGE_PROCESSED_ACCOUNT action', () => {
        const state = {};
        const account = {id: 'account_id'};
        const action = {
            type: 'CHANGE_PROCESSED_ACCOUNT',
            account
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            method: 'password',
            processedAccount: account
        });
    });

    it('should handle UPDATE_LOGIN_VALUE action', () => {
        const state = {
            form: {
                loginError: 'error.1',
                isForceOTP: true
            }
        };
        const action = {
            type: 'UPDATE_LOGIN_VALUE',
            value: 'login'
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            form: {
                login: 'login',
                loginError: 'error.1',
                isForceOTP: false
            },
            loginError: ''
        });
    });

    it('should handle UPDATE_LOGIN_VALUE action without new login', () => {
        const state = {
            form: {
                login: 'old_login',
                loginError: 'error.1',
                isForceOTP: true
            }
        };
        const action = {
            type: 'UPDATE_LOGIN_VALUE'
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            form: {
                login: '',
                loginError: null,
                isForceOTP: false
            },
            loginError: ''
        });
    });

    it('should handle UPDATE_LOGIN_VALUE action with same login', () => {
        const state = {
            form: {
                login: 'old_login',
                loginError: 'error.1',
                isForceOTP: true
            }
        };
        const action = {
            type: 'UPDATE_LOGIN_VALUE',
            value: 'old_login'
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            form: {
                login: 'old_login',
                loginError: 'error.1',
                isForceOTP: true
            },
            loginError: ''
        });
    });

    it('should handle UPDATE_PASSWORD_VALUE action', () => {
        const state = {};
        const action = {
            type: 'UPDATE_PASSWORD_VALUE',
            value: 'password'
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            form: {
                password: 'password'
            },
            passwordError: ''
        });
    });

    it('should handle UPDATE_CAPTCHA_VALUE action', () => {
        const state = {};
        const action = {
            type: 'UPDATE_CAPTCHA_VALUE',
            value: 'captcha_answer'
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            form: {
                captcha_answer: 'captcha_answer'
            },
            captchaError: ''
        });
    });

    it('should handle CHANGE_ACTIVE_ACCOUNT action', () => {
        const state = {};
        const action = {
            type: 'CHANGE_ACTIVE_ACCOUNT',
            uid: 'uid'
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            authorizedAccountsDefaultUid: 'uid'
        });
    });

    it('should handle LOGIN_SUGGESTED_ACCOUNT action', () => {
        const state = {};
        const account = {
            preferred_auth_method: 'password'
        };
        const action = {
            type: 'LOGIN_SUGGESTED_ACCOUNT',
            account
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            method: 'password',
            processedAccount: account
        });
    });

    it('should handle INPUT_LOGIN_SUCCESS action', () => {
        const state = {
            inputLogins: {
                first_login: {}
            }
        };
        const action = {
            type: 'INPUT_LOGIN_SUCCESS',
            inputLogin: {second_login: {}}
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            inputLogins: {
                first_login: {},
                second_login: {}
            }
        });
    });

    it('should handle SHOW_ACCOUNTS_SUCCESS action', () => {
        const state = {};
        const action = {
            type: 'SHOW_ACCOUNTS_SUCCESS',
            accounts: {
                authorizedAccounts: ['authorizedAccounts'],
                authorizedAccountsDefaultUid: ['authorizedAccountsDefaultUid'],
                unitedAccounts: ['unitedAccounts'],
                suggestedAccounts: ['suggestedAccounts']
            }
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            authorizedAccounts: ['authorizedAccounts'],
            authorizedAccountsDefaultUid: ['authorizedAccountsDefaultUid'],
            unitedAccounts: ['unitedAccounts'],
            suggestedAccounts: ['suggestedAccounts']
        });
    });

    it('should handle SHOW_ACCOUNTS_FAIL action', () => {
        const state = {};
        const action = {
            type: 'SHOW_ACCOUNTS_FAIL'
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            errors: {},
            loading: false
        });
    });

    it('should handle SWITCH_TO_MODE_ADDING_ACCOUNT action', () => {
        const state = {};
        const action = {
            type: 'SWITCH_TO_MODE_ADDING_ACCOUNT'
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            mode: 'addingAccount'
        });
    });

    it('should handle SWITCH_TO_MODE_EDIT action', () => {
        const state = {};
        const action = {
            type: 'SWITCH_TO_MODE_EDIT'
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            mode: 'edit'
        });
    });

    it('should handle SWITCH_TO_MODE_WELCOME action', () => {
        const state = {};
        const action = {
            type: 'SWITCH_TO_MODE_WELCOME'
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            mode: 'welcome'
        });
    });

    it('should handle SETUP_MODE action', () => {
        const state = {};
        const action = {
            type: 'SETUP_MODE',
            mode: 'mode'
        };

        const result = authReducer(state, action);

        expect(result).toEqual({
            mode: 'mode'
        });
    });

    it('should handle CHANGE_CAPTCHA_STATE action', () => {
        const state = {};

        let action = {
            type: 'CHANGE_CAPTCHA_STATE',
            isCaptchaRequired: true
        };

        let result = authReducer(state, action);

        expect(result).toEqual({
            isCaptchaRequired: true
        });

        action = {
            type: 'CHANGE_CAPTCHA_STATE',
            isCaptchaRequired: false
        };

        result = authReducer(state, action);

        expect(result).toEqual({
            isCaptchaRequired: false
        });
    });

    it('should handle FORCE_OTP_METHOD action', () => {
        const state = {};

        let action = {
            type: 'FORCE_OTP_METHOD',
            isForceOTP: true
        };

        let result = authReducer(state, action);

        expect(result).toEqual({
            form: {
                isForceOTP: true
            }
        });

        action = {
            type: 'FORCE_OTP_METHOD',
            isForceOTP: false
        };

        result = authReducer(state, action);

        expect(result).toEqual({
            form: {
                isForceOTP: false
            }
        });
    });

    it('should handle DOMIK_IS_LOADING action', () => {
        const state = {};

        let action = {
            type: 'DOMIK_IS_LOADING',
            loading: true
        };

        let result = authReducer(state, action);

        expect(result).toEqual({
            loading: true
        });

        action = {
            type: 'DOMIK_IS_LOADING',
            loading: false
        };

        result = authReducer(state, action);

        expect(result).toEqual({
            loading: false
        });
    });

    it('should handle UNKNOWN_ACTION action', () => {
        const state = 'old_state';
        const action = {
            type: 'UNKNOWN_ACTION'
        };

        const result = authReducer(state, action);

        expect(result).toEqual(state);
    });

    it('should handle fallback state', () => {
        const action = {
            type: 'UNKNOWN_ACTION'
        };

        const result = authReducer(undefined, action);

        expect(result).toEqual({});
    });
});
