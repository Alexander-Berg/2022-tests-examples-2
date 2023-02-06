import processError from '../process_error';
import {updateError} from '../../actions';
import reloadCaptcha from '@components/Captcha/actions/reloadCaptcha';

jest.mock('../../actions', () => ({
    updateError: jest.fn()
}));

jest.mock('@components/Captcha/actions/reloadCaptcha');

const dispatch = jest.fn();

const {location} = window;

describe('processError', () => {
    afterEach(function() {
        reloadCaptcha.mockClear();
        updateError.mockClear();
    });

    it('should dispatch updateError', () => {
        processError('global')(dispatch);
        expect(updateError).toBeCalled();
    });

    it('should be called with global error if error not defined', () => {
        processError('global')(dispatch);
        expect(updateError).toBeCalledWith({field: 'global', message: i18n('Profile.addresses.errors.internal')});
    });

    it('should dispatch reloadCaptcha if captcha error', () => {
        processError('captcha', 'captcha.not_matched')(dispatch);
        expect(reloadCaptcha).toBeCalled();
    });

    it('should do nothing if password.required error', () => {
        processError('password', 'password.required')(dispatch);
        expect(reloadCaptcha).not.toBeCalled();
        expect(updateError).not.toBeCalled();
    });
    it('should redirect to "/auth" if "account.disabled" error;', () => {
        delete window.location;
        window.location = {
            href: 'some url'
        };

        processError('question', 'account.disabled')(dispatch);
        expect(window.location.href).toEqual('/auth');
        window.location = location;
    });
});
