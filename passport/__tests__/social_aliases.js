import aliases from '../social_aliases';

describe('Auth social aliases', () => {
    it('should return social aliases object', () => {
        expect(typeof aliases).toBe('object');
    });
});
