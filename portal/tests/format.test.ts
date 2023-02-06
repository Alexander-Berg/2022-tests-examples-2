import { format } from '../format';

describe('format', function() {
    test('Форматирует значения хтмл', function() {
        expect(format('')).toEqual('');
        expect(format('a')).toEqual('a');

        expect(format(null)).toEqual('');
        expect(format(undefined)).toEqual('');

        expect(format(0)).toEqual('0');
        expect(format(1)).toEqual('1');

        expect(format(false)).toEqual('false');
        expect(format(true)).toEqual('true');

        expect(format({})).toEqual('');
        expect(format(['a', 'b'])).toEqual('');
    });
});
