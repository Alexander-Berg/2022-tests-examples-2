import {joinString, splitStr, toInt, toNumber} from '_pkg/utils/parser';

describe('utils/parser', function () {
    test('toInt', () => {
        expect(toInt('1')).toBe(1);
        expect(toInt(1)).toBe(1);
        expect(toInt('1.1')).toBe(1);
        expect(toInt('a')).toBeUndefined();
    });

    test('toNumber', () => {
        expect(toNumber('1')).toBe(1);
        expect(toNumber(0)).toBe(0);
        expect(toNumber(undefined)).toBeUndefined();
        expect(toNumber(1.1)).toBeCloseTo(1.1);
        expect(toNumber('1.1')).toBeCloseTo(1.1);
    });

    test('splitStr', () => {
        const string = `a
       b
       c`;

        const string2 = `a


       b`;

        expect(splitStr(string)).toHaveLength(3);
        expect(splitStr(string)).toEqual(expect.arrayContaining(['a', 'b', 'c']));
        expect(splitStr(string, [], true)).toHaveLength(3);
        expect(splitStr(string, [], true)).toEqual(expect.arrayContaining(['a', 'b', 'c']));

        expect(splitStr(string2)).toHaveLength(2);
        expect(splitStr(string2)).toEqual(expect.arrayContaining(['a', 'b']));
        expect(splitStr(string2)).not.toContain('');
        expect(splitStr(string2, [], true)).toHaveLength(4);
        expect(splitStr(string2, [], true)).toEqual(expect.arrayContaining(['a', 'b', '']));

        expect(splitStr('a')).toHaveLength(1);
        expect(splitStr('a')).toContain('a');
        expect(splitStr('', [], true)).toHaveLength(0);
        expect(splitStr(' ')).toBeUndefined();
        expect(splitStr(' ', [])).toHaveLength(0);
        expect(splitStr(' ', [], true)).toHaveLength(1);
        expect(splitStr(' ', [], true)).toContain('');

        expect(splitStr('a,b,c', [], true, /,/g)).toEqual(expect.arrayContaining(['a', 'b', 'c']));
        expect(splitStr('a ,b    ,   c   ', [], true, /,/g)).toEqual(expect.arrayContaining(['a', 'b', 'c']));
    });

    test('joinString', () => {
        const string = ` a b c `;
        const strings = ['a', ' g ', ' f '];

        expect(joinString(string)).toEqual('a b c');
        expect(joinString(strings)).toEqual('a, g, f');

        expect(joinString(string, '-')).toEqual('a b c');
        expect(joinString(strings, '-')).toEqual('a-g-f');
    });
});
