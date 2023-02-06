import {describe, expect, it} from 'tests/jest.globals';

import {parseExtension} from './parse-extension';

describe('parse-extension', () => {
    it('should return correct results', () => {
        expect(parseExtension('.')).toBeUndefined();
        expect(parseExtension('.abc')).toBeUndefined();
        expect(parseExtension('abc.')).toBeUndefined();
        expect(parseExtension('.abc.')).toBeUndefined();
        expect(parseExtension('abc')).toBeUndefined();

        expect(parseExtension('abc.zip')).toBe('zip');
        expect(parseExtension('ABC.ZIP')).toBe('zip');
    });
});
