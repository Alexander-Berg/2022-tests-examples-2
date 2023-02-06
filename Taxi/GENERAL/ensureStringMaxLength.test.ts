import {ensureStringMaxLength} from './ensureStringMaxLength';

describe('ensureStringMaxLength', () => {
    it('less than max size', async () => {
        expect(ensureStringMaxLength('abcabcabc', 100)).toBe('abcabcabc');
    });

    it('more than max size', async () => {
        expect(ensureStringMaxLength('abcdef', 5)).toBe('ab...');
    });

    it('empty', async () => {
        expect(ensureStringMaxLength('', 10)).toBe('');
    });
});
