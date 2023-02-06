import {
    parsePhone
} from '../parser';

describe('utils:parsers', () => {
    describe('parsePhone', () => {
        test('Должен вырезать все символы кроме цифр', () => {
            expect(parsePhone('+7 (919) 000-00-00')).toEqual('79190000000');
        });

        test('Цифры обрабатываются без ошибок', () => {
            expect(parsePhone(89190000000)).toEqual('89190000000');
        });

        test('Если цифр нет возвращается пустая строка', () => {
            expect(parsePhone('ab-cd+fe.po')).toEqual('');
        });
    });
});
