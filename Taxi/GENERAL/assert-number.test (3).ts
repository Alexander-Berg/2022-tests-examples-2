import {describe, expect, it} from 'tests/jest.globals';

import {assertNumber} from './assert-number';

describe('assert-number', () => {
    it('should throw if non-number is passed', () => {
        expect(() => assertNumber(NaN)).toThrow();
        expect(() => assertNumber('hello')).toThrow();
        expect(() => assertNumber(undefined)).toThrow();
        expect(() => assertNumber(null)).toThrow();
        expect(() => assertNumber([])).toThrow();
        expect(() => assertNumber({})).toThrow();
    });

    it('should return the right number', () => {
        expect(assertNumber(2)).toBe(2);
        expect(assertNumber(0)).toBe(0);
    });
});
