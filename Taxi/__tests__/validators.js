/* global i18n */ // eslint-disable-line
import {
    isNotEmpty,
    isPositiveNumber,
    isEmail,
    isPhone,
    isAvailablePhone,
    isRussianPhone,
    nullable
} from '../validators';

describe('utils:validators', () => {
    describe('isNotEmpty', () => {
        test('Если не пустая строка - true', () => {
            expect(isNotEmpty('test ')).toBeTruthy();
        });

        test('Если пустая строка - false', () => {
            expect(isNotEmpty(' ')).not.toBeTruthy();
        });

        test('Если не пустой массив - true', () => {
            expect(isNotEmpty([1])).toBeTruthy();
        });

        test('Если пустой массив - false', () => {
            expect(isNotEmpty([])).not.toBeTruthy();
        });

        test('Если не пустой объект - true', () => {
            expect(isNotEmpty({test: 1})).toBeTruthy();
        });

        test('Если пустой объект - false', () => {
            expect(isNotEmpty({})).not.toBeTruthy();
        });

        test('Если null - false', () => {
            expect(isNotEmpty(null)).not.toBeTruthy();
        });

        test('Если 0 - true', () => {
            expect(isNotEmpty(0)).toBeTruthy();
        });
    });

    describe('isPositiveNumber', () => {
        test('Число - true', () => {
            expect(isPositiveNumber(1)).toBeTruthy();
        });

        test('Число как строка - true', () => {
            expect(isPositiveNumber('1')).toBeTruthy();
        });

        test('Дробное число - true', () => {
            expect(isPositiveNumber(1.5)).toBeTruthy();
        });

        test('Дробное число с запятой - true', () => {
            expect(isPositiveNumber('1,5')).toBeTruthy();
        });

        test('Отрицательное число - false', () => {
            expect(isPositiveNumber(-1)).not.toBeTruthy();
        });

        test('Не число - false', () => {
            expect(isPositiveNumber('test')).not.toBeTruthy();
        });

        test('Пустая строка - false', () => {
            expect(isPositiveNumber('')).not.toBeTruthy();
        });
    });

    describe('isEmail', () => {
        test('mail@ya.ru - true', () => {
            expect(isEmail('mail@ya.ru')).toBeTruthy();
        });

        test('mAI0_l@La.rU - true', () => {
            expect(isEmail('mail@ya.ru')).toBeTruthy();
        });

        test('mail@ - false', () => {
            expect(isEmail('mail@')).not.toBeTruthy();
        });

        test('brat-va@почта.рф - true', () => {
            expect(isEmail('brat-va@почта.рф')).toBeTruthy();
        });

        test('1+brat-va@почта.рф - true', () => {
            expect(isEmail('1+brat-va@почта.рф')).toBeTruthy();
        });

        test('brat.va@почта.рф - true', () => {
            expect(isEmail('brat.va@почта.рф')).toBeTruthy();
        });

        test('brat-va@почта.mail.рф - true', () => {
            expect(isEmail('brat-va@почта.mail.рф')).toBeTruthy();
        });

        test('brat-vaпочта.рф - false', () => {
            expect(isEmail('brat-vaпочта.рф')).toBeFalsy();
        });

        test('brat-va@почта.р - false', () => {
            expect(isEmail('brat-va@почта.р')).toBeFalsy();
        });
    });

    describe('isPhone', () => {
        test('+70000000000 - true', () => {
            expect(isPhone('+70000000000')).toBeTruthy();
        });

        test('+7 (000) 000-00-00 - true', () => {
            expect(isPhone('+7 (000) 000-00-00')).toBeTruthy();
        });

        test('Пустое значение возращает false', () => {
            expect(isPhone('')).not.toBeTruthy();
        });

        test('Короткий телефон возращает false', () => {
            expect(isPhone('123213')).not.toBeTruthy();
        });

        test('Не телефон возращает false', () => {
            expect(isPhone('фвфывфыв')).not.toBeTruthy();
        });
    });

    describe('isAvailablePhone', () => {
        test('+70000000000 - false', () => {
            expect(isAvailablePhone('+70000000000')).not.toBeTruthy();
        });

        test('+79000000000 - true', () => {
            expect(isAvailablePhone('+79000000000')).toBeTruthy();
        });

        test('+73000000000 - true', () => {
            expect(isAvailablePhone('+73000000000')).toBeTruthy();
        });

        test('+374000000000 - true', () => {
            expect(isAvailablePhone('+37400000000')).toBeTruthy();
        });

        test('Пустое значение возращает false', () => {
            expect(isAvailablePhone('')).not.toBeTruthy();
        });
    });

    describe('isRussianPhone', () => {
        test('+70000000000 - true', () => {
            expect(isRussianPhone('+70000000000')).toBeTruthy();
        });

        test('Пустое значение возращает false', () => {
            expect(isRussianPhone('')).not.toBeTruthy();
        });

        test('Не российский номер - false', () => {
            expect(isRussianPhone('+38000000000')).toBeFalsy();
        });
    });

    describe('nullable', () => {
        test('Если нет значения, то возвращает тру, если есть, то проверяет валидатором', () => {
            const isValid = jest.fn(val => Boolean(val));
            const isValidOrEmpty = nullable(isValid);

            expect(isValidOrEmpty('')).toBeTruthy();
            expect(isValid).not.toBeCalled();
            expect(isValidOrEmpty('test')).toBeTruthy();
            expect(isValid).toBeCalled();
        });
    });
});
