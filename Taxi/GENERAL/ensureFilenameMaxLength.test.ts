import {ensureFilenameMaxLength} from './ensureFilenameMaxLength';

describe('ensureFilenameMaxLength', () => {
    it('more than max size', async () => {
        expect(ensureFilenameMaxLength('abcabcabc.zip', 100)).toBe('abcabcabc.zip');
    });

    it('correct extension', async () => {
        expect(ensureFilenameMaxLength('abcabcabc.zip', 10)).toBe('ab...c.zip');
        expect(ensureFilenameMaxLength('abc.ext.ext.ext', 10)).toBe('ab...t.ext');
    });

    describe('no extension', () => {
        it('dot', async () => {
            expect(ensureFilenameMaxLength('.', 10)).toBe('.');
        });

        it('nothing', async () => {
            expect(ensureFilenameMaxLength('abcabcabcabc', 10)).toBe('abcabca...');
        });

        it('dot at the end', async () => {
            expect(ensureFilenameMaxLength('abcabcabcabc.', 10)).toBe('abcabca...');
            expect(ensureFilenameMaxLength('abc.xyz.abc.', 10)).toBe('abc.xyz...');
        });

        it('dot at the start', async () => {
            expect(ensureFilenameMaxLength('.abcabcabcabc', 10)).toBe('.abcabc...');
            expect(ensureFilenameMaxLength('.abc.xyz.abc.', 10)).toBe('.abc.xy...');
        });
    });

    it('empty', async () => {
        expect(ensureFilenameMaxLength('', 10)).toBe('');
    });
});
