import { getSearchParams } from '..';

describe('searchParams', () => {
    it('выбрасывает nil/NaN значения', () => {
        expect(
            getSearchParams({ a: null, b: undefined, c: NaN, d: 1 }).toString(),
        ).toBe('d=1');
    });
});
