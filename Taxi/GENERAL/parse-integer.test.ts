import {describe, expect} from 'tests/jest.globals';

import {parseInteger} from './parse-integer';

describe('parse integer from string', () => {
    test('correct cases', () => {
        expect(parseInteger('0')).toEqual(0);
        expect(parseInteger('123')).toEqual(123);
        expect(parseInteger('-1')).toEqual(-1);
    });

    test('wrong cases', () => {
        expect(parseInteger('0x123')).toEqual(undefined);
        expect(parseInteger('abc')).toEqual(undefined);
        expect(parseInteger('100z')).toEqual(undefined);
        expect(parseInteger('25.5')).toEqual(undefined);
        expect(parseInteger('5,123')).toEqual(undefined);
    });
});
