import mapStateToProps from '../mapStateToProps';

describe('Components: PhoneConfirmationPopup.mapStateToProps', () => {
    it('should return valid props', () => {
        const state = {
            phoneConfirm: {
                phoneNumber: 'phone_number',
                confirmationCode: 'confirmationCode',
                isConfirmationCodeSent: 'isConfirmationCodeSent',
                isCaptchaRequired: 'isCaptchaRequired',
                denyResendUntil: 'denyResendUntil',
                errors: 'errors'
            }
        };

        const result = mapStateToProps(state);

        expect(result).toEqual({
            amPhoneNumber: undefined,
            phoneNumber: 'phone_number',
            confirmationCode: 'confirmationCode',
            isConfirmationCodeSent: 'isConfirmationCodeSent',
            isCaptchaRequired: 'isCaptchaRequired',
            denyResendUntil: 'denyResendUntil',
            errors: 'errors',
            confirmationCodeFieldType: 'text',
            hasRoundViewExp: false
        });
    });

    it('should return confirmationCodeFieldType=number in am', () => {
        const state = {
            phoneConfirm: {
                phoneNumber: 'phone_number',
                confirmationCode: 'confirmationCode',
                isConfirmationCodeSent: 'isConfirmationCodeSent',
                isCaptchaRequired: 'isCaptchaRequired',
                denyResendUntil: 'denyResendUntil',
                errors: 'errors'
            },
            am: {
                isAm: true
            }
        };

        const result = mapStateToProps(state);

        expect(result.confirmationCodeFieldType).toEqual('number');
    });
});
