import { UrlUtils } from './UrlUtils';

describe.only('UrlUtils', () => {
    describe('audienceToMetrikaUrl', () => {
        const urls = [
            {
                title: 'beta',
                current: 'https://www-rifler.metrika-dev.haze.yandex.ru',
                expected: 'https://www-rifler.metrika-dev.haze.yandex.ru/',
            },
            {
                title: 'auto-beta',
                current:
                    'https://audience-565.audience.auto-beta.mtrs.yandex.ru',
                expected: 'https://audience-565.auto-beta.mtrs.yandex.ru/',
            },
            {
                title: 'legacy-testing',
                current: 'https://audience.metrika-test.haze.yandex.ru',
                expected: 'https://metrika-test.haze.yandex.ru/',
            },
            {
                title: 'legacy-prestable',
                current: 'https://audience.metrika-ng-ps.yandex.ru',
                expected: 'https://metrika-ng-ps.yandex.ru/',
            },
            {
                title: 'testing',
                current: 'https://test.audience.yandex.ru',
                expected: 'https://test.metrika.yandex.ru',
            },
            {
                title: 'prod',
                current: 'https://audience.yandex.ru',
                expected: 'https://metrika.yandex.ru/',
            },
        ];

        for (const url of urls) {
            it(url.title, () => {
                expect(
                    UrlUtils.audienceToMetrikaUrl(url.current).toString(),
                ).toBe(url.expected);
            });
        }
    });
});
