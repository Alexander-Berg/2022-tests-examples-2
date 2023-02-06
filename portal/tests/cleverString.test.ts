import { cutEndOfString, cutMiddleOfString, cutStartOfString, stringLength, substring } from '../cleverString';

describe('home.cleverString', function() {
    describe('stringLength', function() {
        test('выполняет граничные условия', function() {
            expect(stringLength('')).toEqual(0);

            // @ts-expect-error incorrect args
            expect(stringLength(null)).toEqual(0);

            // @ts-expect-error incorrect args
            expect(stringLength()).toEqual(0);
        });

        test('вычисляет длину простой строки', function() {
            expect(stringLength('aSdFgH')).toEqual(6);

            expect(stringLength('   ')).toEqual(3);
        });

        test('вычисляет длину строки с сурогатными парами', function() {
            expect(stringLength('💩')).toEqual(1);

            expect(stringLength('💩💩💩💩💩')).toEqual(5);

            expect(stringLength('a💩b💩c💩d💩e💩f')).toEqual(11);

            expect(stringLength('💩 : 💩')).toEqual(5);

            expect(stringLength('abc💩def')).toEqual(7);

            expect(stringLength('Iñtërnâtiônàlizætiøn☃💩ab')).toEqual(24);
        });
    });

    describe('substring', function() {
        test('выполняет граничные условия', function() {
            // @ts-expect-error incorrect args
            expect(substring(null, 1, 1)).toBeNull();

            // @ts-expect-error incorrect args
            expect(substring(null)).toBeNull();

            expect(substring('', 0)).toEqual('');
        });

        test('работает на простых строках', function() {
            expect(substring('abcdef', 0)).toEqual('abcdef');

            expect(substring('abcdefg', 3)).toEqual('defg');

            expect(substring('abcdefg', 0, 2)).toEqual('ab');

            expect(substring('abcdefg', 2, 7)).toEqual('cdefg');
        });

        test('работает на строках с сурогатными парами', function() {
            expect(substring('💩-💩-💩', 0)).toEqual('💩-💩-💩');

            expect(substring('💩-💩-💩', 3)).toEqual('-💩');

            expect(substring('💩-💩-💩', 0, 2)).toEqual('💩-');

            expect(substring('💩-💩-💩', 2, 7)).toEqual('💩-💩');

            expect(substring('Iñtërnâtiônàlizætiøn☃💩ab', 20, 3)).toEqual('☃💩a');
        });
    });

    describe('cutMiddleOfString', function() {
        test('выполняет граничные условия', function() {
            // @ts-expect-error incorrect args
            expect(cutMiddleOfString(null, 1)).toBeNull();

            // @ts-expect-error incorrect args
            expect(cutMiddleOfString()).toBeUndefined();

            expect(cutMiddleOfString('', 0, 0)).toEqual('');

            expect(cutMiddleOfString('', 1, 1)).toEqual('');
        });

        test('работает на простых строках', function() {
            expect(cutMiddleOfString('простая string', 7, 6)).toEqual('простая string');

            expect(cutMiddleOfString('простая что-то между string', 7, 6)).toEqual('простая…string');

            expect(cutMiddleOfString('простая string', 5, 0)).toEqual('прост…');

            expect(cutMiddleOfString('простая string', 10, 10)).toEqual('простая string');
        });

        test('работает на строках с сурогатными парами', function() {
            expect(cutMiddleOfString('💩-💩-💩', 0, 0)).toEqual('…');

            expect(cutMiddleOfString('💩-💩-💩', 1, 1)).toEqual('💩…💩');

            expect(cutMiddleOfString('💩-💩-💩', 0, 2)).toEqual('…-💩');

            expect(cutMiddleOfString('💩-💩-💩', 3, 2)).toEqual('💩-💩-💩');

            expect(cutMiddleOfString('Iñtërnâtiônàlizætiøn☃💩ab', 4, 4)).toEqual('Iñtë…☃💩ab');
        });
    });

    describe('cutEndOfString', function() {
        test('выполняет граничные условия', function() {
            // @ts-expect-error incorrect args
            expect(cutEndOfString(null, 1)).toBeNull();

            // @ts-expect-error incorrect args
            expect(cutEndOfString()).toBeUndefined();

            expect(cutEndOfString('', 0)).toEqual('');

            expect(cutEndOfString('', 1)).toEqual('');
        });

        test('работает на простых строках', function() {
            expect(cutEndOfString('простая string', 10)).toEqual('простая s…');

            expect(cutEndOfString('простая string', 13)).toEqual('простая stri…');

            expect(cutEndOfString('простая string', 14)).toEqual('простая string');

            expect(cutEndOfString('простая string', 15)).toEqual('простая string');
        });

        test('работает на строках с сурогатными парами', function() {
            expect(cutEndOfString('💩-💩-💩', 0)).toEqual('');

            expect(cutEndOfString('💩-💩-💩', 1)).toEqual('…');

            expect(cutEndOfString('💩-💩-💩', 3)).toEqual('💩-…');

            expect(cutEndOfString('💩-💩-💩', 4)).toEqual('💩-💩…');

            expect(cutEndOfString('💩-💩-💩', 5)).toEqual('💩-💩-💩');

            expect(cutEndOfString('💩-💩-💩', 6)).toEqual('💩-💩-💩');

            expect(cutEndOfString('Iñtërnâtiônàlizætiøn☃💩ab', 23)).toEqual('Iñtërnâtiônàlizætiøn☃💩…');
        });
    });

    describe('cutStartOfString', function() {
        test('выполняет граничные условия', function() {
            // @ts-expect-error incorrect args
            expect(cutStartOfString(null, 1)).toBeNull();

            // @ts-expect-error incorrect args
            expect(cutStartOfString()).toBeUndefined();

            expect(cutStartOfString('', 0)).toEqual('');

            expect(cutStartOfString('', 1)).toEqual('');
        });

        test('работает на простых строках', function() {
            expect(cutStartOfString('простая string', 10)).toEqual('…ая string');

            expect(cutStartOfString('простая string', 14)).toEqual('простая string');
        });

        test('работает на строках с сурогатными парами', function() {
            expect(cutStartOfString('💩-💩-💩', 0)).toEqual('');

            expect(cutStartOfString('💩-💩-💩', 1)).toEqual('…');

            expect(cutStartOfString('💩-💩-💩', 4)).toEqual('…💩-💩');

            expect(cutStartOfString('💩-💩-💩', 5)).toEqual('💩-💩-💩');

            expect(cutStartOfString('Iñtërnâtiônàlizætiøn☃💩ab', 23)).toEqual('…tërnâtiônàlizætiøn☃💩ab');
        });
    });
});
