import { decline } from '../decline';

describe('decline', function() {
    test('работает со странными вызовами', function() {
        expect(decline(11, [])).toEqual('');
        expect(decline(11, ['молоко'])).toEqual('молоко');
    });

    test('что-то делает при не очень некорректных вызовах', function() {
        expect(decline(-11, ['письмо', 'письма', 'писем'])).toEqual('писем');
    });

    test('работает с корректными вызовами', function() {
        expect(decline(0, ['письмо', 'письма', 'писем'])).toEqual('писем');

        expect(decline(1, ['письмо', 'письма', 'писем'])).toEqual('письмо');

        expect(decline(2, ['письмо', 'письма', 'писем'])).toEqual('письма');
        expect(decline(3, ['письмо', 'письма', 'писем'])).toEqual('письма');
        expect(decline(4, ['письмо', 'письма', 'писем'])).toEqual('письма');

        expect(decline(5, ['письмо', 'письма', 'писем'])).toEqual('писем');
        expect(decline(6, ['письмо', 'письма', 'писем'])).toEqual('писем');
        expect(decline(10, ['письмо', 'письма', 'писем'])).toEqual('писем');

        expect(decline(11, ['письмо', 'письма', 'писем'])).toEqual('писем');
        expect(decline(12, ['письмо', 'письма', 'писем'])).toEqual('писем');
        expect(decline(13, ['письмо', 'письма', 'писем'])).toEqual('писем');
        expect(decline(14, ['письмо', 'письма', 'писем'])).toEqual('писем');

        expect(decline(20, ['письмо', 'письма', 'писем'])).toEqual('писем');
        expect(decline(21, ['письмо', 'письма', 'писем'])).toEqual('письмо');
        expect(decline(22, ['письмо', 'письма', 'писем'])).toEqual('письма');
        expect(decline(23, ['письмо', 'письма', 'писем'])).toEqual('письма');
        expect(decline(25, ['письмо', 'письма', 'писем'])).toEqual('писем');

        expect(decline(100, ['письмо', 'письма', 'писем'])).toEqual('писем');
        expect(decline(101, ['письмо', 'письма', 'писем'])).toEqual('письмо');
        expect(decline(102, ['письмо', 'письма', 'писем'])).toEqual('письма');
        expect(decline(103, ['письмо', 'письма', 'писем'])).toEqual('письма');
        expect(decline(105, ['письмо', 'письма', 'писем'])).toEqual('писем');

        expect(decline(110, ['письмо', 'письма', 'писем'])).toEqual('писем');
        expect(decline(111, ['письмо', 'письма', 'писем'])).toEqual('писем');
        expect(decline(112, ['письмо', 'письма', 'писем'])).toEqual('писем');
        expect(decline(115, ['письмо', 'письма', 'писем'])).toEqual('писем');
        expect(decline(120, ['письмо', 'письма', 'писем'])).toEqual('писем');
        expect(decline(121, ['письмо', 'письма', 'писем'])).toEqual('письмо');
        expect(decline(122, ['письмо', 'письма', 'писем'])).toEqual('письма');
        expect(decline(125, ['письмо', 'письма', 'писем'])).toEqual('писем');

        expect(decline(0, ['письмо', 'письма', 'писем', 'пусто'])).toEqual('пусто');
        expect(decline(1, ['письмо', 'письма', 'писем', 'пусто'])).toEqual('письмо');
        expect(decline(2, ['письмо', 'письма', 'писем', 'пусто'])).toEqual('письма');
        expect(decline(5, ['письмо', 'письма', 'писем', 'пусто'])).toEqual('писем');
    });
});
