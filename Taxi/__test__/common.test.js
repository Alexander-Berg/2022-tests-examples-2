import {withoutUndefinedKeys, toArray, isEmptyValue, getIndexesOf} from '../common';

describe('utils:common', () => {
    test('withoutUndefinedKeys', () => {
        const IS_NOT_UNDEFINED = {
            filled1: 'filled1',
            filled2: '',
            filled3: 0,
            filled4: 1,
            filled5: null
        };

        expect(
            withoutUndefinedKeys({
                ...IS_NOT_UNDEFINED,
                undefined: undefined
            })
        ).toEqual(IS_NOT_UNDEFINED);
    });

    test('toArray', () => {
        expect(toArray(1)).toEqual([1]);
        expect(toArray([1])).toEqual([1]);
    });

    test('isEmptyValue', () => {
        expect(isEmptyValue('')).toBe(true);
        expect(isEmptyValue(null)).toBe(true);
        expect(isEmptyValue()).toBe(true);
        expect(isEmptyValue([])).toBe(true);
        expect(isEmptyValue(['', null])).toBe(true);
        expect(isEmptyValue(0)).toBe(false);
        expect(isEmptyValue(1)).toBe(false);
        expect(isEmptyValue('1')).toBe(false);
        expect(isEmptyValue([null, 1])).toBe(false);
    });

    test('getIndexesOf', () => {
        const SEARCH = 'test';
        const TEXT = `${SEARCH} два ${SEARCH} два два три ${SEARCH}`;

        expect(getIndexesOf('', TEXT)).toEqual([]);
        expect(getIndexesOf(SEARCH, TEXT)).toEqual([0, 9, 26]);
    });
});
