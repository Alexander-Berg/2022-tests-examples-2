import mapStateToProps from '../mapStateToProps';
import processPasswordError from '../processPasswordError';

jest.mock('../../../../metrics', () => ({
    send: jest.fn()
}));

jest.mock('../processPasswordError', () => jest.fn(() => 'passwordError'));

describe('Components: OTPField.mapStateToProps', () => {
    it('should return valid props', () => {
        const state = {
            auth: {
                passwordError: 'passwordError',
                form: {
                    login: 'formLogin',
                    password: 'password'
                }
            },
            common: {
                restorePasswordUrl: 'restorePasswordUrl',
                restorePasswordCaptchaUrl: 'restorePasswordCaptchaUrl'
            }
        };

        let result = mapStateToProps(state);

        expect(result.fieldError).toBe('passwordError');
        expect(processPasswordError).toBeCalled();
        expect(processPasswordError.mock.calls[0][0]).toBe('passwordError');
        expect(result.fieldLink.url).toBe('restorePasswordCaptchaUrl?login=formLogin');
        expect(result.fieldLink.text).toBe(i18n('_AUTH_.restore_access'));

        state.auth.form.login = null;
        result = mapStateToProps(state);
        expect(result.fieldLink.url).toBe('restorePasswordUrl');
    });
});
