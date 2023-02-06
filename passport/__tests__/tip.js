import {checkForNumbersAndCases} from '../tip.js';

describe('Morda.Forms.Password.PasswordTip', () => {
    describe('checkForNumbersAndCases', () => {
        it('should return false', () => {
            expect(checkForNumbersAndCases('asdf')).toBe(false);
        });
        it('should return true', () => {
            expect(checkForNumbersAndCases('Aa0')).toBe(true);
        });
    });
});
