import errors from '../errors';

describe('Auth errors', () => {
    it('should return errors object', () => {
        expect(typeof errors).toBe('object');
    });
});
