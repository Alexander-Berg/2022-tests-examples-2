import errors from '../../../errors';
import processPasswordError from '../processPasswordError';

describe('processPasswordError', () => {
    it('should process password error', () => {
        let result = processPasswordError();

        expect(result).toBe('');

        result = processPasswordError('captcha.required');
        expect(result).toBe('');

        result = processPasswordError('account.disabled');
        expect(result).toBe('_AUTH_.account.disabled_detailed');

        result = processPasswordError('password.not_matched');
        expect(result).toBe('_AUTH_.Errors.otp.not_matched');

        result = processPasswordError('login.long', {url: 'yandex.ru', text: 'link'});
        expect(result).toBe('_AUTH_.login_errors_incorrect');

        result = processPasswordError('unknown.error', {url: 'yandex.ru', text: 'link'});
        expect(result).toBe('_AUTH_.Errors.internal');

        errors['unknown.error'] = 'Unknown error.';
        result = processPasswordError('unknown.error', {url: 'yandex.ru', text: 'link'});
        expect(result).toBe('Unknown error');
    });
});
