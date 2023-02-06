import {NumberParseResult, toNumberSafely} from '../parser';

const fail = (): NumberParseResult => {
    return {
        type: 'fail'
    };
};

const done = (value: number): NumberParseResult => {
    return {
        type: 'done',
        value
    };
};

describe('parser', () => {
    test('toNumberSafely', () => {
        expect(toNumberSafely(null)).toEqual(fail());
        expect(toNumberSafely(undefined)).toEqual(fail());
        expect(toNumberSafely('')).toEqual(fail());
        expect(toNumberSafely(' ')).toEqual(fail());
        expect(toNumberSafely('test')).toEqual(fail());
        expect(toNumberSafely('10 test')).toEqual(fail());
        expect(toNumberSafely('10.09 test')).toEqual(fail());
        expect(toNumberSafely('-10.09 test')).toEqual(fail());
        expect(toNumberSafely('0')).toEqual(done(0));
        expect(toNumberSafely('10')).toEqual(done(10));
        expect(toNumberSafely('-10')).toEqual(done(-10));
        expect(toNumberSafely('-0.9')).toEqual(done(-0.9));
        expect(toNumberSafely('0.9')).toEqual(done(0.9));
        expect(toNumberSafely(0)).toEqual(done(0));
        expect(toNumberSafely(10)).toEqual(done(10));
        expect(toNumberSafely(-10)).toEqual(done(-10));
        expect(toNumberSafely(-0.9)).toEqual(done(-0.9));
        expect(toNumberSafely(0.9)).toEqual(done(0.9));
    });
});
