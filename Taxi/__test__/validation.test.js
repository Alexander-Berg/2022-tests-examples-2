import {isValidEmail} from '../validation';

describe('method isValidEmail', () => {
    const VALID_EMAIL = 'ivanov@yandex.ru';
    const UNVALID_EMAIL = '@y.ry';

    test('expected email', () => {
        expect(isValidEmail(VALID_EMAIL)).toBeTruthy();
    });

    test('unexpected email', () => {
        expect(isValidEmail(UNVALID_EMAIL)).toBeFalsy();
    });
});
