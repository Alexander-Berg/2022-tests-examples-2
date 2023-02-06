import {describe, expect, it} from 'tests/jest.globals';

import {formatFileSize} from './convert-file-size';

describe('formatFileSize', () => {
    it('formats zero and negative values', async () => {
        expect(formatFileSize(0)).toBe('0.00b');
        expect(formatFileSize(-1000)).toBe('0.00b');
    });

    it('formats large values greater that 99gb', async () => {
        expect(formatFileSize(99 * 1024 * 1024 * 1024 + 1)).toBe('>99gb');
    });

    describe('size as number', () => {
        it('formats correctly', async () => {
            expect(formatFileSize(10)).toBe('10.00b');
            expect(formatFileSize(1200)).toBe('1.17kb');
            expect(formatFileSize(1900)).toBe('1.86kb');
            expect(formatFileSize(948577)).toBe('926.34kb');
            expect(formatFileSize(1048577)).toBe('1.00mb');
            expect(formatFileSize(3694577)).toBe('3.52mb');
            expect(formatFileSize(99999999999)).toBe('93.13gb');
        });

        it('formats with provided suffix', async () => {
            expect(formatFileSize(10, 'b')).toBe('10.00b');
            expect(formatFileSize(1200, 'b')).toBe('1200.00b');
            expect(formatFileSize(1000, 'kb')).toBe('0.98kb');
            expect(formatFileSize(11000, 'mb')).toBe('0.01mb');
            expect(formatFileSize(11000000, 'gb')).toBe('0.01gb');
        });
    });

    describe('size as string', () => {
        it('formats correctly', async () => {
            expect(formatFileSize('10b')).toBe('10.00b');
            expect(formatFileSize('1200mb')).toBe('1.17gb');
            expect(formatFileSize('1900b')).toBe('1.86kb');
            expect(formatFileSize('948577b')).toBe('926.34kb');
            expect(formatFileSize('1048577b')).toBe('1.00mb');
            expect(formatFileSize('3694577kb')).toBe('3.52gb');
            expect(formatFileSize('99999999999b')).toBe('93.13gb');
        });

        it('formats with provided suffix', async () => {
            expect(formatFileSize('10b', 'b')).toBe('10.00b');
            expect(formatFileSize('1200kb', 'mb')).toBe('1.17mb');
            expect(formatFileSize('98gb', 'mb')).toBe('100352.00mb');
            expect(formatFileSize('11000b', 'mb')).toBe('0.01mb');
            expect(formatFileSize('11000000b', 'gb')).toBe('0.01gb');
        });
    });
});
