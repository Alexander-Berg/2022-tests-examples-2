import {lower, upper} from '../toSafeCase';

describe('toSafeCase', () => {
    it('should return lowercase string', () => {
        expect(lower('String')).toEqual('string');
    });

    it('should return uppercase string', () => {
        expect(upper('string')).toEqual('STRING');
    });

    it('should return empty string if argument is invalid', () => {
        expect(lower()).toEqual('');
        expect(lower(undefined)).toEqual('');
        expect(lower(null)).toEqual('');
        expect(lower('')).toEqual('');
        expect(lower(false)).toEqual('');
        expect(lower(0)).toEqual('');
    });
});
