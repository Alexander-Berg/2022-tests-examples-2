import * as actions from '../actions';

describe('delete actions', () => {
    it('should return type TOGGLE_MODAL', () => {
        expect(actions.setModalStatus(true)).toEqual({
            type: actions.TOGGLE_MODAL,
            status: true
        });
    });

    it('should return type UPDATE_ERROR', () => {
        const data = {
            field: 'captcha',
            message: 'Контрольные символы введены неправильно'
        };

        expect(actions.updateError(data)).toEqual({
            type: actions.UPDATE_ERROR,
            errorData: {
                field: 'captcha',
                message: 'Контрольные символы введены неправильно'
            }
        });
    });

    it('should return type CHECK_STATUS', () => {
        expect(actions.checkStatus('code_sent')).toEqual({
            type: actions.CHECK_STATUS,
            status: 'code_sent'
        });
    });

    it('should return type CONFIRM_PHONE_CODE', () => {
        expect(actions.confirmPhoneCodeSend(30)).toEqual({
            type: actions.CONFIRM_PHONE_CODE,
            resend: 30
        });
    });

    it('should return type UPDATE_FORM_DATA', () => {
        const fields = {
            code: '123'
        };

        expect(actions.updateFormDataFields(fields)).toEqual({
            type: actions.UPDATE_FORM_DATA,
            fields
        });
    });

    it('should return type IS_FETCHING', () => {
        expect(actions.setFetchingStatus(true)).toEqual({
            type: actions.IS_FETCHING,
            isFetching: true
        });
    });
});
