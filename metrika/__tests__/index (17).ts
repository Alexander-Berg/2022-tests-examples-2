import { getRedirectUrl } from '..';

const ADM_HOST = 'admetrica.yandex.';

const C_HOST = 'media.metrica.yandex.';
const K_HOST = 'media.metrika.yandex.';

describe('domain-redirect (k => c)', () => {
    it('works for prod domain (com)', () => {
        const url = getRedirectUrl(`https://${K_HOST}com`, K_HOST, 'com');
        expect(url).toBe(`https://${C_HOST}com/`);
    });

    it('works for prod domain (com.tr)', () => {
        const url = getRedirectUrl(`https://${K_HOST}com.tr`, K_HOST, 'com.tr');
        expect(url).toBe(`https://${C_HOST}com.tr/`);
    });

    it('saves protocol, path and params (com.tr)', () => {
        const url = getRedirectUrl(
            `http://branch_name.dev.${K_HOST}com.tr/path/to?a=b`,
            K_HOST,
            'com.tr',
        );

        expect(url).toBe(`http://branch_name.dev.${C_HOST}com.tr/path/to?a=b`);
    });
});

describe('domain-redirect (c => k)', () => {
    it('works for prod domain (ru)', () => {
        const url = getRedirectUrl(`https://${C_HOST}ru`, C_HOST, 'ru');
        expect(url).toBe(`https://${K_HOST}ru/`);
    });

    it('works for prod domain (kz)', () => {
        const url = getRedirectUrl(`https://${C_HOST}kz`, C_HOST, 'kz');
        expect(url).toBe(`https://${K_HOST}kz/`);
    });

    it('saves protocol, path and params (ru)', () => {
        const url = getRedirectUrl(
            `http://branch_name.dev.${C_HOST}ru/path/to?a=b`,
            C_HOST,
            'ru',
        );

        expect(url).toBe(`http://branch_name.dev.${K_HOST}ru/path/to?a=b`);
    });
});

describe('domain-redirect (admetrica => c/k)', () => {
    it('works for prod domain (ru)', () => {
        const url = getRedirectUrl(`https://${ADM_HOST}ru`, ADM_HOST, 'ru');
        expect(url).toBe(`https://${K_HOST}ru/`);
    });

    it('works for prod domain (com)', () => {
        const url = getRedirectUrl(`https://${ADM_HOST}com`, ADM_HOST, 'com');
        expect(url).toBe(`https://${C_HOST}com/`);
    });

    it('works for sub domain (ru)', () => {
        const url = getRedirectUrl(
            `https://test.${ADM_HOST}ru`,
            ADM_HOST,
            'ru',
        );

        expect(url).toBe(`https://test.${K_HOST}ru/`);
    });

    it('works for sub domain (com)', () => {
        const url = getRedirectUrl(
            `https://test.${ADM_HOST}com`,
            ADM_HOST,
            'com',
        );

        expect(url).toBe(`https://test.${C_HOST}com/`);
    });

    it('works for sub domains (ru)', () => {
        const url = getRedirectUrl(
            `https://branch_name.dev.${ADM_HOST}ru`,
            ADM_HOST,
            'ru',
        );

        expect(url).toBe(`https://branch_name.dev.${K_HOST}ru/`);
    });

    it('works for sub domains (com.tr)', () => {
        const url = getRedirectUrl(
            `https://branch_name.dev.${ADM_HOST}com.tr`,
            ADM_HOST,
            'com.tr',
        );

        expect(url).toBe(`https://branch_name.dev.${C_HOST}com.tr/`);
    });

    it('saves protocol, path and params (ru)', () => {
        const url = getRedirectUrl(
            `http://branch_name.dev.${ADM_HOST}ru/path/to?a=b`,
            ADM_HOST,
            'ru',
        );

        expect(url).toBe(`http://branch_name.dev.${K_HOST}ru/path/to?a=b`);
    });

    it('saves protocol, path and params (kz)', () => {
        const url = getRedirectUrl(
            `http://branch_name.dev.${ADM_HOST}kz/path/to?a=b`,
            ADM_HOST,
            'kz',
        );

        expect(url).toBe(`http://branch_name.dev.${K_HOST}kz/path/to?a=b`);
    });

    it('saves protocol, path and params (com)', () => {
        const url = getRedirectUrl(
            `http://branch_name.dev.${ADM_HOST}com/path/to?a=b`,
            ADM_HOST,
            'com',
        );

        expect(url).toBe(`http://branch_name.dev.${C_HOST}com/path/to?a=b`);
    });
});
