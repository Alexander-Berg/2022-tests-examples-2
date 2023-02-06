import {formatPhone} from '../text-utils';

describe('utils:text-utils', () => {
    describe('formatPhone', () => {
        test('replace all unnecessary spaces', () => {
            expect(formatPhone(' + 7 0 1 2 3 4 5 6 7 8 9 ')).toBe('+7 012 34 56 789');
        });
        test('adds plus', () => {
            expect(formatPhone(' 7 0 1 2 3 4 5 6 7 8 9 ')).toBe('+7 012 34 56 789');
        });
    });
});
