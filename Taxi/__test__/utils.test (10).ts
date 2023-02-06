import {isValidSymbols} from '../utils';

describe('isValidSymbols', () => {
    it('должен возвращаться true для валидных символов(числа, запятые, дефисы, пробелы)', () => {
        const validValues = '1234567890,- ';
        validValues.split('').forEach(symbol => expect(isValidSymbols(symbol)).toBeTruthy());
    });

    it('должен возвращаться false для любых значений отличных от валидных', () => {
        const invalidValues =
            '!@#$%^&*()_=+§±~`/?.><|{}[];:\'"\\' +
            'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM' +
            'йцукенгшщзхъфывапролджэёячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЁЯЧСМИТЬБЮ';
        invalidValues.split('').forEach(symbol => expect(isValidSymbols(symbol)).toBeFalsy());
    });
});
