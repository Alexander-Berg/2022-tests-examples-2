import {
    clearErrors,
    setErrors,
    changeCaptchaAnswer,
    changeCaptchaState,
    changePhoneNumber,
    changeEmail,
    changeConfirmationCode,
    sentPhoneConfirmationCodeSuccess,
    sentEmailConfirmationCodeSuccess,
    changeConfirmationCodeSentStatus
} from '../additionalDataRequestActions';

describe('Actions: additionalDataRequestActions', () => {
    test('should return clear errors type', () => {
        expect(clearErrors()).toEqual({type: 'CLEAR_ERRORS'});
    });

    test('should return set errors type and errors list', () => {
        const errors = ['error.1', 'error.2'];

        expect(setErrors(errors)).toEqual({type: 'SET_ERRORS', errors});
    });

    test('should return change captcha type and new captcha answer', () => {
        const captchaAnswer = '1234';

        expect(changeCaptchaAnswer(captchaAnswer)).toEqual({type: 'CHANGE_CAPTCHA_ANSWER', captchaAnswer});
    });

    test('should return change captcha state type and new captcha required flag', () => {
        const isCaptchaRequired = true;

        expect(changeCaptchaState(isCaptchaRequired)).toEqual({type: 'CHANGE_CAPTCHA_STATE', isCaptchaRequired});
    });

    test('should return change phone number type and new phone number', () => {
        const phoneNumber = '+71234567890';

        expect(changePhoneNumber(phoneNumber)).toEqual({type: 'CHANGE_PHONE_NUMBER', phoneNumber});
    });

    test('should return change email type and new email', () => {
        const email = 'new@email.ru';

        expect(changeEmail(email)).toEqual({type: 'CHANGE_EMAIL', email});
    });

    test('should return change confirmation code type and new confirmation code', () => {
        const confirmationCode = '1234';

        expect(changeConfirmationCode(confirmationCode)).toEqual({type: 'CHANGE_CONFIRMATION_CODE', confirmationCode});
    });

    test('should return success sent phone confirm code type and response payload', () => {
        const payload = {
            number: {
                original: '+7 123 456 789 0'
            },
            deny_resend_until: 1
        };

        expect(sentPhoneConfirmationCodeSuccess(payload)).toEqual({
            type: 'SENT_PHONE_CONFIRMATION_CODE_SUCCESS',
            payload
        });
    });

    test('should return success sent email confirm code type', () => {
        expect(sentEmailConfirmationCodeSuccess()).toEqual({type: 'SENT_EMAIL_CONFIRMATION_CODE_SUCCESS'});
    });

    test('should return success sent email confirm code type', () => {
        expect(changeConfirmationCodeSentStatus(false)).toEqual({
            type: 'CHANGE_CONFIRMATION_CODE_SENT_STATUS',
            isConfirmationCodeSent: false
        });
    });
});
