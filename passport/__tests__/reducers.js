import {
    CHANGE_CAPTCHA_ANSWER,
    CHANGE_CAPTCHA_STATE,
    CHANGE_PHONE_NUMBER,
    CHANGE_EMAIL,
    CHANGE_CONFIRMATION_CODE,
    CHANGE_CONFIRMATION_CODE_SENT_STATUS,
    SENT_PHONE_CONFIRMATION_CODE_SUCCESS,
    SENT_EMAIL_CONFIRMATION_CODE_SUCCESS,
    CLEAR_ERRORS,
    SET_ERRORS
} from '../actions';
import additionalDataRequest from '../reducers';

const reducer = additionalDataRequest;

describe('Reducer: additionalDataRequest', () => {
    it('should define default state', () => {
        const defaultState = {};

        expect(reducer(undefined, {type: 'DEFAULT_ACTION'})).toEqual(defaultState);
    });

    it('should return default state', () => {
        const state = {};

        expect(reducer(state, {type: 'DEFAULT_ACTION'})).toEqual(state);
    });

    it('should change captcha answer', () => {
        const state = {captchaAnswer: 'old_answer'};
        const newCaptchaAnswer = 'new_answer';
        const newState = reducer(state, {type: CHANGE_CAPTCHA_ANSWER, captchaAnswer: newCaptchaAnswer});

        expect(newState.captchaAnswer).toEqual(newCaptchaAnswer);
    });

    it('should change captcha state', () => {
        const state = {isCaptchaRequired: false};
        const newCaptchaState = true;
        const newState = reducer(state, {type: CHANGE_CAPTCHA_STATE, isCaptchaRequired: newCaptchaState});

        expect(newState.isCaptchaRequired).toEqual(newCaptchaState);
    });

    it('should change phone number', () => {
        const state = {
            phone: {
                number: '+7'
            }
        };
        const newPhoneNumber = '+7 123 456 789 0';
        const newState = reducer(state, {type: CHANGE_PHONE_NUMBER, phoneNumber: newPhoneNumber});

        expect(newState.phone.number).toEqual(newPhoneNumber);
    });

    it('should change email', () => {
        const state = {email: 'old@email.ru'};
        const newEmail = 'new@email.ru';
        const newState = reducer(state, {type: CHANGE_EMAIL, email: newEmail});

        expect(newState.email).toEqual(newEmail);
    });

    it('should change confirmation code', () => {
        const state = {confirmationCode: '1234'};
        const newConfirmationCode = '5678';
        const newState = reducer(state, {type: CHANGE_CONFIRMATION_CODE, confirmationCode: newConfirmationCode});

        expect(newState.confirmationCode).toEqual(newConfirmationCode);
    });

    it('should change confirmation code sent flag after send mail', () => {
        const state = {isConfirmationCodeSent: false};
        const newState = reducer(state, {type: SENT_EMAIL_CONFIRMATION_CODE_SUCCESS});

        expect(newState.isConfirmationCodeSent).toBe(true);
    });

    it('should change phone number, timer and confirmation code sent flag after send sms', () => {
        const state = {
            phone: {
                number: '+71234567890'
            },
            isConfirmationCodeSent: false
        };
        const payload = {
            number: {
                original: '+7 123 456 789 0'
            },
            deny_resend_until: 1
        };
        const newState = reducer(state, {type: SENT_PHONE_CONFIRMATION_CODE_SUCCESS, payload});

        expect(newState.phone.number).toEqual(payload.number.original);
        expect(newState.denyResendUntil).toEqual(payload.deny_resend_until * 1000);
        expect(newState.isConfirmationCodeSent).toBe(true);
    });

    it('should remove all errors', () => {
        const state = {
            errors: ['error.1', 'error.2']
        };
        const newState = reducer(state, {type: CLEAR_ERRORS});

        expect(newState.errors).toEqual([]);
    });

    it('should set new errors', () => {
        const state = {
            errors: ['error.1', 'error.2']
        };
        const newErrors = ['error.3', 'error.4'];
        const newState = reducer(state, {type: SET_ERRORS, errors: newErrors});

        expect(newState.errors).toEqual(newErrors);
    });

    it('should set captcha required flag', () => {
        const state = {
            isCaptchaRequired: false,
            errors: []
        };
        const newErrors = ['captcha.required'];
        const newState = reducer(state, {type: SET_ERRORS, errors: newErrors});

        expect(newState.isCaptchaRequired).toBe(true);
    });

    it('should change confirmation code sent flag', () => {
        const state = {isConfirmationCodeSent: true};
        const newState = reducer(state, {type: CHANGE_CONFIRMATION_CODE_SENT_STATUS, isConfirmationCodeSent: false});

        expect(newState.isConfirmationCodeSent).toBe(false);
    });
});
