import deleteAccount from '../reducers';
import * as actions from '../actions';

describe('delete account reducers', () => {
    it('should set isModalOpened to true', () => {
        const modalAction = actions.setModalStatus(true);

        expect(deleteAccount({}, modalAction)).toEqual({isModalOpened: true});
    });

    it('should set form fields', () => {
        const captchaPassedAction = actions.updateFormDataFields({captcha: 'testcaptcha'});

        expect(deleteAccount({}, captchaPassedAction)).toEqual({form: {captcha: 'testcaptcha'}});
    });

    it('should update error', () => {
        const updateErrorAction = actions.updateError({
            field: 'captcha',
            message: 'контрольные символы введены неправильно'
        });

        expect(deleteAccount({}, updateErrorAction)).toEqual({
            error: {field: 'captcha', message: 'контрольные символы введены неправильно'}
        });
    });

    it('should update confirmation status', () => {
        const checkStatusAction = actions.checkStatus('code_sent');

        expect(deleteAccount({}, checkStatusAction)).toEqual({confirmation: {status: 'code_sent'}});
    });

    it('should update phone confirmation', () => {
        const confirmCodeAction = actions.confirmPhoneCodeSend(30);

        expect(deleteAccount({}, confirmCodeAction)).toEqual({confirmation: {countdown: 30}});
    });

    it('should update fetchingStatus', () => {
        const fetchingStatusAction = actions.setFetchingStatus(true);

        expect(deleteAccount({}, fetchingStatusAction)).toEqual({isFetching: true});
    });
});
