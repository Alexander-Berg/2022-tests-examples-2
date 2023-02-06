import {isNumber, isNotEmpty, isPositiveInt, isUniq, isEmail, isPhone, isOneOf, isNumberInRange} from '_pkg/utils/validators';

describe('utils/validators', function () {
    test('isPositiveNumber', () => {
        expect(isNumber(1)).toBeTruthy();
        expect(isNumber(0)).toBeTruthy();
        expect(isNumber(0.1)).toBeTruthy();

        expect(isNumber('1')).toBeTruthy();
        expect(isNumber('0')).toBeTruthy();
        expect(isNumber('0.1')).toBeTruthy();

        expect(isNumber('a')).toBeFalsy();
        expect(isNumber(-1)).toBeFalsy();
        expect(isNumber('-1')).toBeFalsy();
    });

    test('isPositiveInt', () => {
        expect(isPositiveInt(1)).toBeTruthy();
        expect(isPositiveInt(100)).toBeTruthy();
        expect(isPositiveInt('1')).toBeTruthy();

        expect(isPositiveInt(0.1)).toBeFalsy();
        expect(isPositiveInt('a')).toBeFalsy();
        expect(isPositiveInt()).toBeFalsy();
        expect(isPositiveInt(0)).toBeFalsy();
        expect(isPositiveInt(-1)).toBeFalsy();
    });

    test('isNotEmpty', () => {
        expect(isNotEmpty('a')).toBeTruthy();
        expect(isNotEmpty(' a ')).toBeTruthy();
        expect(isNotEmpty(['a'])).toBeTruthy();
        expect(isNotEmpty({a: 1})).toBeTruthy();
        expect(isNotEmpty(1)).toBeTruthy();
        expect(isNotEmpty(0)).toBeTruthy();
        expect(isNotEmpty(new File([], 'test'))).toBeTruthy();

        expect(isNotEmpty('')).toBeFalsy();
        expect(isNotEmpty('  ')).toBeFalsy();
        expect(isNotEmpty([])).toBeFalsy();
        expect(isNotEmpty({})).toBeFalsy();
        expect(isNotEmpty()).toBeFalsy();
    });

    test('isUniq', () => {
        expect(isUniq('a')).toBeTruthy();
        expect(isUniq([{a: 1}, {a: 2}, {a: 3}], {a: 1}, 'a')).toBeTruthy();
        expect(isUniq([{a: 1}, {a: 2}, {a: 3}], {b: 1}, 'b')).toBeTruthy();

        expect(isUniq([{a: 1}, {a: 2}, {a: 2}], {a: 2}, 'a')).toBeFalsy();
        expect(isUniq([{a: 1}, {a: 2}, {a: 3}], {a: 1}, 'b')).toBeFalsy();
    });

    test('isEmail', () => {
        expect(isEmail('a@b.ru')).toBeTruthy();
        // т.к. eamil неоязательное поле его отсутвие, считаем валидным значением
        expect(isEmail()).toBeTruthy();
        expect(isEmail('')).toBeTruthy();

        expect(isEmail('89191111111@yandex.ru')).toBeTruthy();
        expect(isEmail('маша@yandex.info')).toBeTruthy();

        expect(isEmail('a')).toBeFalsy();
        expect(isEmail('a@')).toBeFalsy();
        expect(isEmail('a@')).toBeFalsy();
        expect(isEmail(1)).toBeFalsy();
        expect(isEmail('1')).toBeFalsy();
        expect(isEmail('a.ru')).toBeFalsy();
        expect(isEmail('a@a.a')).toBeFalsy();
    });

    test('isPhone', () => {
        expect(isPhone('+79001112233')).toBeTruthy();
        expect(isPhone('+00000000000')).toBeTruthy();
        expect(isPhone('+000000000001')).toBeTruthy();
        expect(isPhone('+00000000000111222')).toBeTruthy();

        expect(isPhone('+00000000')).toBeFalsy();
        expect(isPhone('000000000')).toBeFalsy();
        expect(isPhone('+qwertyuiopq')).toBeFalsy();
        expect(isPhone(123)).toBeFalsy();
    });

    test('isOneOf', () => {
        let isOneOfOneOrTwo = isOneOf(['one', 'two']);

        expect(isOneOfOneOrTwo('one')).toBeTruthy();
        expect(isOneOfOneOrTwo('two')).toBeTruthy();

        expect(isOneOfOneOrTwo('three')).toBeFalsy();
        expect(isOneOfOneOrTwo(3)).toBeFalsy();

        isOneOfOneOrTwo = isOneOf([1, 2]);
        expect(isOneOfOneOrTwo(1)).toBeTruthy();
        expect(isOneOfOneOrTwo(2)).toBeTruthy();

        expect(isOneOfOneOrTwo(3)).toBeFalsy();
        expect(isOneOfOneOrTwo('3')).toBeFalsy();
    });

    test('isNumberInRange', () => {
        expect(isNumberInRange(0, 1)(0.4)).toBeTruthy();
        expect(isNumberInRange(10, 228)(228)).toBeTruthy();
        expect(isNumberInRange(-100, 100)(-20)).toBeTruthy();

        expect(isNumberInRange(0, 1)(-1)).toBeFalsy();
        expect(isNumberInRange(0, 0.3)(0.4)).toBeFalsy();
    });
});
