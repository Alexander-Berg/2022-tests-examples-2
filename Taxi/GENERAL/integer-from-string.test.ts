import {describe, expect} from 'tests/jest.globals';

import {integerFromString} from './integer-from-string';

describe('validate integer from string', () => {
    const struct = integerFromString();

    test('correct cases', () => {
        expect(struct.create('0')).toEqual(0);
        expect(struct.create('123')).toEqual(123);
        expect(struct.create('-1')).toEqual(-1);
    });

    test('wrong cases', () => {
        expect(() => struct.create('0x123')).toThrow('Expected an integer, but received: "0x123"');
        expect(() => struct.create('abc')).toThrow('Expected an integer, but received: "abc"');
        expect(() => struct.create('100z')).toThrow('Expected an integer, but received: "100z"');
        expect(() => struct.create('25.5')).toThrow('Expected an integer, but received: "25.5"');
        expect(() => struct.create('5,123')).toThrow('Expected an integer, but received: "5,123"');
    });
});
