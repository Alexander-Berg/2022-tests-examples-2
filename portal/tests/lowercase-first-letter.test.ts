import { lowercaseFirstLetter } from '../lowercase-first-letter';

describe('lowercase-first-letter', () => {
    test('test', () => {
        expect(lowercaseFirstLetter('')).toEqual('');
        expect(lowercaseFirstLetter('a')).toEqual('a');
        expect(lowercaseFirstLetter('A')).toEqual('a');
        expect(lowercaseFirstLetter('-')).toEqual('-');
        expect(lowercaseFirstLetter('Abcde abcde')).toEqual('abcde abcde');
        expect(lowercaseFirstLetter('Леса дремучие')).toEqual('леса дремучие');
    });
});
