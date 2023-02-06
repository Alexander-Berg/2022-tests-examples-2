import {describe, expect} from 'tests/jest.globals';

import subtractArraysImmutable from './subtract-arrays-immutable';

describe('subtract arrays in immutable way', () => {
    test('it should be immutable', () => {
        const source = [1];
        const subtrahend: number[] = [];
        const subtracted = subtractArraysImmutable(source, subtrahend);
        expect(source).toEqual(subtracted);
        expect(source).not.toBe(subtracted);
    });

    test('it should subtract elements', () => {
        const source = [1, 1, 1, 2, 3];
        expect(subtractArraysImmutable(source, [1, 2, 3])).toEqual([1, 1]);
        expect(subtractArraysImmutable(source, [1, 2, 2, 2, 3])).toEqual([1, 1]);
        expect(subtractArraysImmutable(source, [])).toEqual(source);
        expect(subtractArraysImmutable([], source)).toEqual([]);
    });
});
