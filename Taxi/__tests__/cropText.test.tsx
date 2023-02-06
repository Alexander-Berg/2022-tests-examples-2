import {cropText} from '../cropText';

describe('cropText tests', () => {
    test('it must return the same string (less than max length)', () => {
        expect(cropText('')).toStrictEqual('');
        expect(cropText('1234')).toStrictEqual('1234');
        expect(cropText('1234 asdfasdf', {maxLength: 40})).toStrictEqual('1234 asdfasdf');
    });

    test('it must return the cropped string (more than max length)', () => {
        expect(cropText('123', {maxLength: 2})).toStrictEqual('123');
        expect(cropText('1234', {maxLength: 1})).toStrictEqual('1...');
    });

    test('it must return the same string (text length is less, than end of string)', () => {
        expect(cropText('12', {maxLength: 2})).toStrictEqual('12');
    });

    test('it must return the cropped string with other end', () => {
        const endOfString = '_';

        expect(cropText('123', {endOfString})).toStrictEqual('123');
        expect(cropText('1234', {maxLength: 2, endOfString})).toStrictEqual('12_');
        expect(cropText('1234 asdfasdf', {maxLength: 40, endOfString})).toStrictEqual('1234 asdfasdf');
    });
});
