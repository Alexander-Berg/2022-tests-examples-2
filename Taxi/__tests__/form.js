import {maskByCountriesCode, getPhoneMask, validateModel, checkValidity} from '../form';
import {isNotEmpty} from '../validators';

describe('utils:form', () => {
    describe('getPhoneMask', () => {
        test('Пустой телефон должен возвращать маску по умолчанию', () => {
            expect(getPhoneMask()).toBe('+9 999 999-99-9999');
        });

        test('Неизвестный телефон должен возвращать маску по умолчанию', () => {
            expect(getPhoneMask('+00000000000')).toBe('+9 999 999-99-9999');
        });

        test('Телефон ввиде числа не должен выдавать ошибку', () => {
            expect(() => {
                getPhoneMask(1);
            }).not.toThrow();
        });

        test('Украинский телефон возвращает маску для Украины', () => {
            expect(getPhoneMask('+380 234')).toBe(maskByCountriesCode.ua.mask);
        });
    });

    describe('Валидация форм', () => {
        const validModel = {ticket: 'TXI-3000'};
        const invalidModel = {ticket: ''};
        const partialValidModel = {ticket: 'SOME-3000'};
        const validators = {ticket: isNotEmpty};
        const nestedValidators = {
            ticket: {
                isNotEmpty,
                isTXI: val => val.includes('TXI')
            }
        };

        describe('validateModel', () => {
            test('Для невалидных данных validateModel должен выставлять флаг true', () => {
                expect(validateModel(validModel, validators).ticket).toBeFalsy();
                expect(validateModel(invalidModel, validators).ticket).toBeTruthy();
            });

            test('С вложенными валидаторами', () => {
                expect(validateModel(validModel, nestedValidators).ticket.isNotEmpty).toBeFalsy();
                expect(validateModel(validModel, nestedValidators).ticket.isTXI).toBeFalsy();
                expect(validateModel(invalidModel, nestedValidators).ticket.isNotEmpty).toBeTruthy();
                expect(validateModel(invalidModel, nestedValidators).ticket.isTXI).toBeTruthy();
                expect(validateModel(partialValidModel, nestedValidators).ticket.isNotEmpty).toBeFalsy();
                expect(validateModel(partialValidModel, nestedValidators).ticket.isTXI).toBeTruthy();
            });
        });

        describe('checkValidity', () => {
            test('Если есть невалидные поля - false', () => {
                expect(checkValidity(validateModel(validModel, validators))).toBeTruthy();
                expect(checkValidity(validateModel(invalidModel, validators))).toBeFalsy();
                expect(checkValidity(validateModel(validModel, nestedValidators))).toBeTruthy();
                expect(checkValidity(validateModel(invalidModel, nestedValidators))).toBeFalsy();
                expect(checkValidity(validateModel(partialValidModel, nestedValidators))).toBeFalsy();
            });
        });
    });
});
