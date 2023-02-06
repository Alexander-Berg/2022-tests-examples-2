import {hasDriverWithoutValue, isIntInRange, isValidValues} from '../utils';

describe('Проверка функции isIntInRange', () => {
    it('Проверка пограничных значений', () => {
        expect(isIntInRange(0, 0, 100)).toEqual(true);
        expect(isIntInRange(100, 0, 100)).toEqual(true);
        expect(isIntInRange('0', 0, 100)).toEqual(true);
        expect(isIntInRange('100', 0, 100)).toEqual(true);
    });
    it('Проверка на выход из диапозона', () => {
        expect(isIntInRange(-1, 0, 100)).toEqual(false);
        expect(isIntInRange(101, 0, 100)).toEqual(false);
        expect(isIntInRange('-1', 0, 100)).toEqual(false);
        expect(isIntInRange('101', 0, 100)).toEqual(false);
    });
});

describe('Проверка функции isValidDriverValues', () => {
    it('Корректный udid со значением', () => {
        expect(isValidValues('sdfFhg46 89\nsdFEhdjj 100\nsdf3F_f 0')).toEqual(true);
    });
    it('Корректный udid без значения', () => {
        expect(isValidValues('sdf3df_sdf\nsdfsd/df-s\n_3dfs3FDd')).toEqual(true);
    });
    it('Некорректный udid', () => {
        expect(isValidValues('sdfseПрав\nsdfhyti=s')).toEqual(false);
    });
    it('Лишние пробелы в строке', () => {
        expect(isValidValues('sdfssdf sdfs 78\nssdfDF3  89\nfdsgfjk ')).toEqual(false);
    });
    it('value меньше 0', () => {
        expect(isValidValues('sdfsde -1\nsdfee3')).toEqual(false);
    });
    it('value не целое число', () => {
        expect(isValidValues('sdfssdf 10.1\ndfddg')).toEqual(false);
    });
});

describe('Проверка функции hasDriverWithoutValue', () => {
    it('Содержит udid без value', () => {
        expect(hasDriverWithoutValue(isValidValues, 'sdfssdf 45\nsdfsdf\nsdfssdd 4')).toEqual(true);
    });
    it('Не содержит udid без value', () => {
        expect(hasDriverWithoutValue(isValidValues, 'sdfss 2\nsdsddf 100\nssdddf 0\ndhhdfjkf 55')).toEqual(false);
    });
});
