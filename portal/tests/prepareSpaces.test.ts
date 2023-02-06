/* eslint dot-notation: 0, no-unused-expressions: 0 */

import {
    prepareSpaces, prepareSpacesAroundHyphen,
    prepareSpacesBeforeShortEnding, prepareSpacesFull,
    prepareSpacesInDigits,
    prepareSpacesInPunctuation
} from '../prepareSpaces';

describe('prepareSpaces', function() {
    test('пробел после предлога', function() {
        expect(prepareSpaces('')).toEqual('');
        expect(prepareSpaces('   ')).toEqual('   ');
        expect(prepareSpaces('abc')).toEqual('abc');
        expect(prepareSpaces('a b')).toEqual('a&nbsp;b');
        expect(prepareSpaces('a Ё')).toEqual('a&nbsp;Ё');
        expect(prepareSpaces('Её ноутбук')).toEqual('Её&nbsp;ноутбук');
        expect(prepareSpaces('abc bcd')).toEqual('abc bcd');
        expect(prepareSpaces('a bcd')).toEqual('a&nbsp;bcd');
        expect(prepareSpaces('Abc something as abc a bcd')).toEqual('Abc something as&nbsp;abc a&nbsp;bcd');
        expect(prepareSpaces('Квартиры на ул. Мосфильмовская, 1 https://yandex.ru')).toEqual('Квартиры на&nbsp;ул. Мосфильмовская, 1 https://yandex.ru');
    });
});

describe('prepareSpaces.digits', function() {
    test('пробел внутри числа', function() {
        expect(prepareSpacesInDigits('')).toEqual('');
        expect(prepareSpacesInDigits('  ')).toEqual('  ');
        expect(prepareSpacesInDigits('a b')).toEqual('a b');
        expect(prepareSpacesInDigits('1 000')).toEqual('1&nbsp;000');
        expect(prepareSpacesInDigits('21 50')).toEqual('21&nbsp;50');
        expect(prepareSpacesInDigits('12 345 678')).toEqual('12&nbsp;345&nbsp;678');
        expect(prepareSpacesInDigits('abc 1 234')).toEqual('abc 1&nbsp;234');
        expect(prepareSpacesInDigits('34 56 abc 1 234 d fre')).toEqual('34&nbsp;56 abc 1&nbsp;234 d fre');
    });
});

describe('prepareSpaces.punctuation', function() {
    test('пробел перед знаками пунктуации', function() {
        expect(prepareSpacesInPunctuation('')).toEqual('');
        expect(prepareSpacesInPunctuation('  ')).toEqual('  ');
        expect(prepareSpacesInPunctuation('a b')).toEqual('a b');
        expect(prepareSpacesInPunctuation('ab!')).toEqual('ab!');
        expect(prepareSpacesInPunctuation('a , ')).toEqual('a&nbsp;, ');
        expect(prepareSpacesInPunctuation('abc ! dfgh')).toEqual('abc&nbsp;! dfgh');
        expect(prepareSpacesInPunctuation('abc  !')).toEqual('abc  !');
        expect(prepareSpacesInPunctuation('Abc :) deh ! 1 dfh - d fre  !')).toEqual('Abc&nbsp;:) deh&nbsp;! 1 dfh&nbsp;- d fre  !');
        expect(prepareSpacesInPunctuation('<hl>Натяжной</hl> <hl>потолок</hl> -<hl>Звездное</hl> <hl>небо</hl>. Жми!'))
            .toEqual('<hl>Натяжной</hl> <hl>потолок</hl> -<hl>Звездное</hl> <hl>небо</hl>. Жми!');
    });
});

describe('prepareSpaces.shortEnding', function() {
    test('пробел перед коротким словом в конце предложения', function() {
        expect(prepareSpacesBeforeShortEnding('')).toEqual('');
        expect(prepareSpacesBeforeShortEnding('  ')).toEqual('  ');
        expect(prepareSpacesBeforeShortEnding('a b')).toEqual('a&nbsp;b');
        expect(prepareSpacesBeforeShortEnding('ab!')).toEqual('ab!');
        expect(prepareSpacesBeforeShortEnding('a , ')).toEqual('a , ');
        expect(prepareSpacesBeforeShortEnding('a 22')).toEqual('a&nbsp;22');
        expect(prepareSpacesBeforeShortEnding('a р.')).toEqual('a&nbsp;р.');
    });
});

describe('prepareSpaces.aroundHyphen', function() {
    test('пробел перед коротким словом в конце предложения', function() {
        expect(prepareSpacesAroundHyphen('')).toEqual('');
        expect(prepareSpacesAroundHyphen('  ')).toEqual('  ');
        expect(prepareSpacesAroundHyphen('a-b')).toEqual('<nobr>a-b</nobr>');
        expect(prepareSpacesAroundHyphen('ab!')).toEqual('ab!');
        expect(prepareSpacesAroundHyphen('a - b')).toEqual('a - b');
        expect(prepareSpacesAroundHyphen('в р-не')).toEqual('в <nobr>р-не</nobr>');
    });
});

describe('prepareSpaces.full', function() {
    test('пробелы в числах, после предлогов, перед знаками пунктуации - все вместе', function() {
        expect(prepareSpacesFull('')).toEqual('');
        expect(prepareSpacesFull('  ')).toEqual('  ');
        expect(prepareSpacesFull('a b')).toEqual('a&nbsp;b');
        expect(prepareSpacesFull('ab!')).toEqual('ab!');
        expect(prepareSpacesFull('a , ')).toEqual('a&nbsp;, ');
        expect(prepareSpacesFull('abc ! dfgh')).toEqual('abc&nbsp;! dfgh');
        expect(prepareSpacesFull('Abc :) deh ! 1 345 dfh - d fre  !')).toEqual('Abc&nbsp;:) deh&nbsp;! 1&nbsp;345 dfh&nbsp;- d&nbsp;fre  !');
        expect(prepareSpacesFull('Abc :) deh ! 1 345 d-fh - d fre d')).toEqual('Abc&nbsp;:) deh&nbsp;! 1&nbsp;345 <nobr>d-fh</nobr>&nbsp;- d&nbsp;fre&nbsp;d');
    });
});
