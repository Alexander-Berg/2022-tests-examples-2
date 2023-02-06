import {parseArrayDataFromString} from '../parseArrayDataFromString';

describe('parseArrayDataFromString', () => {
    it('Возвращает пустой массив при вставке пустых значений', () => {
        expect(parseArrayDataFromString('')).toEqual([]);
        expect(parseArrayDataFromString('     ,  ;    \n   ')).toEqual([]);
    });

    it('Возвращает массив строк используя дефолтные разделители', () => {
        expect(parseArrayDataFromString('one two')).toEqual(['one', 'two']);
        expect(parseArrayDataFromString('    one   two   ')).toEqual(['one', 'two']);
        expect(parseArrayDataFromString('    one,   two ')).toEqual(['one', 'two']);
        expect(parseArrayDataFromString('    one,   two ;, three  four  \n five, ')).toEqual([
            'one',
            'two',
            'three',
            'four',
            'five',
        ]);
    });

    it('Возвращает массив строк используя заданные разделители', () => {
        expect(parseArrayDataFromString('one-two---three__five', /-|_/)).toEqual(['one', 'two', 'three', 'five']);
    });
});
