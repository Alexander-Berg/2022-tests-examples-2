import {
    domikIsLoading,
    updateLoginValue,
    changeProcessedAccount,
    updatePasswordValue,
    updateCaptchaValue,
    updateTokensSuccess,
    canRegister,
    setupBackPane,
    setLoginError,
    setPasswordError,
    setCaptchaError,
    setMagicError,
    changeCaptchaState,
    setupMode,
    forceOTPMethod,
    changeMobileMenuVisibility,
    changeMobileMenuType,
    setProccessedAccountUid,
    setAuthMailSent,
    setAuthMailConfirmed,
    changePagePopupType,
    changePagePopupVisibility,
    setAuthMailError,
    loginSuggestedAccountSuccess,
    inputLoginSuccess,
    showAccountsSuccess,
    showAccountsFail,
    switchToModeAddingAccountSuccess,
    switchToModeEditSuccess,
    switchToModeMagicSuccess,
    switchToModeWelcomeSuccess,
    redirectToRetpathSuccess,
    redirectToBackpathSuccess,
    redirect,
    initAdditionalDataRequest,
    updateAuthMailStatus,
    setMagicLinkDisabled
} from '../';

describe('Actions: Index', () => {
    it('should return action type DOMIK_IS_LOADING', () => {
        let result = domikIsLoading(false);

        expect(result).toEqual({
            type: 'DOMIK_IS_LOADING',
            loading: false
        });

        result = domikIsLoading(true);

        expect(result).toEqual({
            type: 'DOMIK_IS_LOADING',
            loading: true
        });
    });

    it('should return action type UPDATE_LOGIN_VALUE', () => {
        const result = updateLoginValue('login');

        expect(result).toEqual({
            type: 'UPDATE_LOGIN_VALUE',
            value: 'login'
        });
    });

    it('should return action type CHANGE_PROCESSED_ACCOUNT', () => {
        const result = changeProcessedAccount({id: 'account_id'});

        expect(result).toEqual({
            type: 'CHANGE_PROCESSED_ACCOUNT',
            account: {id: 'account_id'}
        });
    });

    it('should return action type UPDATE_PASSWORD_VALUE', () => {
        const result = updatePasswordValue('password');

        expect(result).toEqual({
            type: 'UPDATE_PASSWORD_VALUE',
            value: 'password'
        });
    });

    it('should return action type UPDATE_CAPTCHA_VALUE', () => {
        const result = updateCaptchaValue('captcha');

        expect(result).toEqual({
            type: 'UPDATE_CAPTCHA_VALUE',
            value: 'captcha'
        });
    });

    it('should return action type UPDATE_TOKENS_SUCCESS', () => {
        const result = updateTokensSuccess('track', 'csrf');

        expect(result).toEqual({
            type: 'UPDATE_TOKENS_SUCCESS',
            track_id: 'track',
            csrf_token: 'csrf'
        });
    });

    it('should return action type CAN_REGISTER', () => {
        const result = canRegister({
            isCanRegister: true,
            registrationLogin: 'registrationLogin',
            registrationType: 'registrationType',
            registrationPhoneNumber: 'registrationPhoneNumber',
            registrationCountry: 'registrationCountry'
        });

        expect(result).toEqual({
            type: 'CAN_REGISTER',
            isCanRegister: true,
            registrationLogin: 'registrationLogin',
            registrationType: 'registrationType',
            registrationPhoneNumber: 'registrationPhoneNumber',
            registrationCountry: 'registrationCountry'
        });
    });

    it('should return action type SETUP_BACK_PANE', () => {
        const result = setupBackPane('backPane');

        expect(result).toEqual({
            type: 'SETUP_BACK_PANE',
            pane: 'backPane'
        });
    });

    it('should return action type SET_LOGIN_ERROR', () => {
        const result = setLoginError('error');

        expect(result).toEqual({
            type: 'SET_LOGIN_ERROR',
            error: 'error'
        });
    });

    it('should return action type SET_PASSWORD_ERROR', () => {
        const result = setPasswordError('error');

        expect(result).toEqual({
            type: 'SET_PASSWORD_ERROR',
            error: 'error'
        });
    });

    it('should return action type SET_CAPTCHA_ERROR', () => {
        const result = setCaptchaError('error');

        expect(result).toEqual({
            type: 'SET_CAPTCHA_ERROR',
            error: 'error'
        });
    });

    it('should return action type SET_MAGIC_ERROR', () => {
        const result = setMagicError('error');

        expect(result).toEqual({
            type: 'SET_MAGIC_ERROR',
            error: 'error'
        });
    });

    it('should return action type CHANGE_CAPTCHA_STATE', () => {
        let result = changeCaptchaState(false);

        expect(result).toEqual({
            type: 'CHANGE_CAPTCHA_STATE',
            isCaptchaRequired: false
        });

        result = changeCaptchaState(true);

        expect(result).toEqual({
            type: 'CHANGE_CAPTCHA_STATE',
            isCaptchaRequired: true
        });
    });

    it('should return action type SETUP_MODE', () => {
        const result = setupMode('mode');

        expect(result).toEqual({
            type: 'SETUP_MODE',
            mode: 'mode'
        });
    });

    it('should return action type FORCE_OTP_METHOD', () => {
        let result = forceOTPMethod(true);

        expect(result).toEqual({
            type: 'FORCE_OTP_METHOD',
            isForceOTP: true
        });

        result = forceOTPMethod(false);

        expect(result).toEqual({
            type: 'FORCE_OTP_METHOD',
            isForceOTP: false
        });
    });

    it('should return action type CHANGE_MOBILE_MENU_VISIBILITY', () => {
        const result = changeMobileMenuVisibility('visible');

        expect(result).toEqual({
            type: 'CHANGE_MOBILE_MENU_VISIBILITY',
            visible: 'visible'
        });
    });

    it('should return action type CHANGE_MOBILE_MENU_TYPE', () => {
        const result = changeMobileMenuType('mobileMenuType');

        expect(result).toEqual({
            type: 'CHANGE_MOBILE_MENU_TYPE',
            mobileMenuType: 'mobileMenuType'
        });
    });

    it('should return action type CHANGE_PAGE_POPUP_VISIBILITY', () => {
        const result = changePagePopupVisibility('visible');

        expect(result).toEqual({
            type: 'CHANGE_PAGE_POPUP_VISIBILITY',
            visible: 'visible'
        });
    });

    it('should return action type CHANGE_PAGE_POPUP_TYPE', () => {
        const result = changePagePopupType('popupType');

        expect(result).toEqual({
            type: 'CHANGE_PAGE_POPUP_TYPE',
            pagePopupType: 'popupType'
        });
    });

    it('should return action type SET_PROCESSED_ACCOUNT_UID', () => {
        const result = setProccessedAccountUid('processedAccountUid');

        expect(result).toEqual({
            type: 'SET_PROCESSED_ACCOUNT_UID',
            processedAccountUid: 'processedAccountUid'
        });
    });

    it('should return action type AUTH_MAIL_SENT', () => {
        const result = setAuthMailSent(['1', '2', '3']);

        expect(result).toEqual({
            type: 'AUTH_MAIL_SENT',
            code: ['1', '2', '3']
        });
    });

    it('should return action type AUTH_MAIL_CONFIRMED', () => {
        const result = setAuthMailConfirmed('retpath');

        expect(result).toEqual({
            type: 'AUTH_MAIL_CONFIRMED',
            retpath: 'retpath'
        });
    });

    it('should return action type SET_AUTH_MAIL_ERROR', () => {
        const result = setAuthMailError('error');

        expect(result).toEqual({
            type: 'SET_AUTH_MAIL_ERROR',
            error: 'error'
        });
    });

    it('should return action type SET_AUTH_MAIL_UPDATED', () => {
        const result = updateAuthMailStatus(true);

        expect(result).toEqual({
            type: 'SET_AUTH_MAIL_UPDATED',
            isUpdated: true
        });
    });

    it('should return action type SET_AUTH_MAIL_UPDATED', () => {
        const result = setMagicLinkDisabled();

        expect(result).toEqual({
            type: 'SET_AUTH_MAIL_DISABLED'
        });
    });

    it('should return action type LOGIN_SUGGESTED_ACCOUNT', () => {
        const result = loginSuggestedAccountSuccess({id: 'account_id'});

        expect(result).toEqual({
            type: 'LOGIN_SUGGESTED_ACCOUNT',
            account: {id: 'account_id'}
        });
    });

    it('should return action type INPUT_LOGIN_SUCCESS', () => {
        const result = inputLoginSuccess('login');

        expect(result).toEqual({
            type: 'INPUT_LOGIN_SUCCESS',
            inputLogin: 'login'
        });
    });

    it('should return action type SHOW_ACCOUNTS_SUCCESS', () => {
        const result = showAccountsSuccess({
            unitedAccounts: [],
            proccessedAccount: {}
        });

        expect(result).toEqual({
            type: 'SHOW_ACCOUNTS_SUCCESS',
            accounts: {
                unitedAccounts: [],
                proccessedAccount: {}
            }
        });
    });

    it('should return action type SHOW_ACCOUNTS_FAIL', () => {
        const result = showAccountsFail(['error.1', 'error.2']);

        expect(result).toEqual({
            type: 'SHOW_ACCOUNTS_FAIL',
            errors: ['error.1', 'error.2']
        });
    });

    it('should return action type SWITCH_TO_MODE_ADDING_ACCOUNT', () => {
        const result = switchToModeAddingAccountSuccess();

        expect(result).toEqual({
            type: 'SWITCH_TO_MODE_ADDING_ACCOUNT'
        });
    });

    it('should return action type SWITCH_TO_MODE_EDIT', () => {
        const result = switchToModeEditSuccess();

        expect(result).toEqual({
            type: 'SWITCH_TO_MODE_EDIT'
        });
    });

    it('should return action type SWITCH_TO_MODE_MAGIC', () => {
        const result = switchToModeMagicSuccess(false);

        expect(result).toEqual({
            type: 'SWITCH_TO_MODE_MAGIC',
            isFromLoginSuggest: false
        });
    });

    it('should return action type SWITCH_TO_MODE_WELCOME', () => {
        const result = switchToModeWelcomeSuccess();

        expect(result).toEqual({
            type: 'SWITCH_TO_MODE_WELCOME'
        });
    });

    it('should return action type REDIRECT_TO_RETPATH', () => {
        const result = redirectToRetpathSuccess();

        expect(result).toEqual({
            type: 'REDIRECT_TO_RETPATH'
        });
    });

    it('should return action type REDIRECT_TO_BACKPATH', () => {
        const result = redirectToBackpathSuccess();

        expect(result).toEqual({
            type: 'REDIRECT_TO_BACKPATH'
        });
    });

    it('should return action type INIT_ADDITIONAL_DATA_REQUEST', () => {
        const payload = {foo: 'bar'};
        const result = initAdditionalDataRequest(payload);

        expect(result).toEqual({
            type: 'INIT_ADDITIONAL_DATA_REQUEST',
            payload
        });
    });

    it('should handle redirect', () => {
        const submitFn = jest.fn();
        const appendChildFn = jest.fn();
        const removeChildFn = jest.fn();
        const createElementFn = jest.fn(() => ({
            appendChild: appendChildFn,
            submit: submitFn,
            parentNode: {
                removeChild: removeChildFn
            }
        }));

        Object.defineProperty(global.document, 'createElement', {value: createElementFn});
        Object.defineProperty(global.document.body, 'appendChild', {value: appendChildFn});

        redirect('/profile');

        expect(appendChildFn).toBeCalled();
        expect(submitFn).toBeCalled();
    });
});
