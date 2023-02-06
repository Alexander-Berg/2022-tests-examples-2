import mapStateToProps from '../mapStateToProps';

describe('Components: EmailRequestPage.mapStateToProps', () => {
    it('should return valid props', () => {
        const state = {
            additionalDataRequest: {
                email: 'email',
                confirmationCode: 'confirmationCode',
                isConfirmationCodeSent: 'isConfirmationCodeSent',
                isCaptchaRequired: 'isCaptchaRequired',
                action: 'action',
                denyResendUntil: 'denyResendUntil',
                errors: 'errors'
            }
        };

        const result = mapStateToProps(state);

        expect(result).toEqual({
            email: 'email',
            confirmationCode: 'confirmationCode',
            isConfirmationCodeSent: 'isConfirmationCodeSent',
            isCaptchaRequired: 'isCaptchaRequired',
            action: 'action',
            denyResendUntil: 'denyResendUntil',
            errors: 'errors'
        });
    });
});
