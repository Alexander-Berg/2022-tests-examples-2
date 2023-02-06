import mapStateToProps from '../mapStateToProps';

describe('Components: PhoneConfirmationPopup.mapStateToProps', () => {
    it('should return valid props', () => {
        const state = {
            additionalDataRequest: {
                phone: {
                    id: 'phone_id',
                    number: 'phone_number'
                },
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
            confirmationCode: 'confirmationCode',
            isConfirmationCodeSent: 'isConfirmationCodeSent',
            isCaptchaRequired: 'isCaptchaRequired',
            action: 'action',
            denyResendUntil: 'denyResendUntil',
            errors: 'errors',
            phoneNumber: 'phone_number',
            popupTitle: '_AUTH_.phone.enter-confirmation-code.title.v2',
            phoneId: 'phone_id',
            isWithCodeFormatExp: true
        });
    });
});
