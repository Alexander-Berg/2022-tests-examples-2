import {describe, expect, it} from 'tests/jest.globals';

import {getRegion, replaceRegion} from './region';

describe('getRegion', () => {
    it('empty', () => {
        expect(getRegion('')).toBeUndefined();
    });

    it('root', () => {
        expect(getRegion('/')).toBeUndefined();
    });

    it('ok', () => {
        expect(getRegion('ru')).toBe('ru');
        expect(getRegion('/ru')).toBe('ru');
        expect(getRegion('/ru/')).toBe('ru');
    });
});

describe('replaceRegion', () => {
    it('empty path', () => {
        expect(replaceRegion('', 'ru')).toBe('');
    });

    it('empty newRegion', () => {
        expect(replaceRegion('ru', '')).toBe('ru');
    });

    it('root', () => {
        expect(replaceRegion('/', 'ru')).toBe('/');
    });

    it('ok', () => {
        expect(replaceRegion('ru', 'fr')).toBe('fr');
        expect(replaceRegion('/ru/abc/ru/z', 'fr')).toBe('/fr/abc/ru/z');
    });
});
