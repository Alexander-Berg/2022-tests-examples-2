import { capitalize } from '../capitalize';

describe('capitalize', function() {
    test('не изменяет пустую строку', function() {
        expect(capitalize('')).toEqual('');
    });

    test('работает на одной букве', function() {
        expect(capitalize('a')).toEqual('A');
    });

    test('работает на английской строке', function() {
        expect(capitalize('abc')).toEqual('Abc');
    });

    test('работает на русской строке', function() {
        expect(capitalize('петя')).toEqual('Петя');
    });
});
