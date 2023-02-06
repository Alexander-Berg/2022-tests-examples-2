import trimLastDot from '../trimLastDot';

describe('Utils: trimLastDot', () => {
    it('should return string without ended dot', () => {
        const result = trimLastDot('string with dot.');

        expect(result).toBe('string with dot');
    });

    it('should return original string', () => {
        const result = trimLastDot('string without dot');

        expect(result).toBe('string without dot');
    });
});
