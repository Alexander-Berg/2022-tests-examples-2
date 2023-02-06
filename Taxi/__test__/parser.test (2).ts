import {toNumber} from '../parser';

describe('utils/strict/parser', () => {
    test('toNumber', () => {
        expect(toNumber(123)).toEqual(123);
        expect(toNumber(0.4)).toEqual(0.4);
        expect(toNumber(.5)).toEqual(.5);
        expect(toNumber('123')).toEqual(123);
        expect(toNumber('123.5')).toEqual(123.5);
        expect(toNumber('.5')).toEqual(.5);
        expect(toNumber('')).toEqual(undefined);
        expect(toNumber('0')).toEqual(0);
        expect(toNumber(NaN)).toEqual(undefined);
        expect(toNumber(undefined)).toEqual(undefined);
    });
});
