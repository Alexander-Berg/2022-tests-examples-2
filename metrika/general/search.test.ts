import { createSearcher } from '.';

describe('Search util', () => {
    it('searches common strings without params', () => {
        const source = 'ABC';

        expect(createSearcher('ab')(source)).toEqual({
            start: 0,
            end: 2,
        });

        expect(createSearcher('фи')(source)).toEqual({
            start: 0,
            end: 2,
        });

        expect(createSearcher('lol')(source)).toBeUndefined();
    });

    it('searches common strings with options', () => {
        const source = 'ABC';

        expect(
            createSearcher('ab', undefined, { caseSensitive: true })(source),
        ).toBeUndefined();

        expect(
            createSearcher('фи', undefined, { layoutDependent: true })(source),
        ).toBeUndefined();
    });

    it('searches objects without params', () => {
        const source = { name: 'ABC' };

        expect(
            createSearcher<typeof source>('bc', (item) => item.name)(source),
        ).toEqual({
            start: 1,
            end: 3,
        });
    });
});
