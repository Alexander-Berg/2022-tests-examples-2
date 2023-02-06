import {extendUrlWithQueryParams, parseQuery, appendQueryToUrl, createUrl} from '../url';

describe('utils:url', () => {
    describe('extendUrlWithQueryParams', () => {
        test('Прокидываются только допустимые query', () => {
            const host = 'https://test.yandex.ru';
            expect(
                extendUrlWithQueryParams(host, {
                    adj_campaign: 1,
                    adj_adgroup: 'test',
                    adj_creative: true,
                    nowhitelist: true
                })
            ).toBe(`${host}/?adj_campaign=1&adj_adgroup=test&adj_creative=true`);
        });

        test('Исходные query не перетераются', () => {
            const host = 'https://test.yandex.ru';
            expect(
                extendUrlWithQueryParams(`${host}?id=test&adj_campaign=2`, {
                    adj_campaign: 1,
                    adj_adgroup: 'test'
                })
            ).toBe(`${host}/?id=test&adj_campaign=2&adj_adgroup=test`);
        });

        test('Верно работает без протокола', () => {
            const host = '//test.yandex.ru';
            expect(
                extendUrlWithQueryParams(host, {
                    adj_campaign: 1,
                    adj_adgroup: 'test',
                    adj_creative: true,
                    nowhitelist: true
                })
            ).toBe(`${host}/?adj_campaign=1&adj_adgroup=test&adj_creative=true`);
        });
    });

    describe('parseQuery', () => {
        test('Верно парсит query', () => {
            expect(parseQuery('?test=1&var=test&arr=a&arr=b')).toStrictEqual({test: '1', var: 'test', arr: 'b'});
        });
    });

    describe('appendQueryToUrl', () => {
        test('Верно добавляет query параметры в чистый урл', () => {
            const url = 'https://test.yandex.net';
            expect(appendQueryToUrl(url, {test: '1', var: 'test', arr: 'b'})).toBe(`${url}/?test=1&var=test&arr=b`);
        });

        test('Не перетерает существующие query', () => {
            const url = 'https://test.yandex.net/?test=1&a=b';
            expect(appendQueryToUrl(url, {test: '2', var: 'test'})).toBe(`${url}&var=test`);
        });
    });

    describe('createUrl', () => {
        test('Валидная ссылка возвращает верный URL', () => {
            expect(createUrl('https://test.yandex.ru').toString()).toBe('https://test.yandex.ru/');
        });

        test('Невалидная ссылка возвращает исходную строку', () => {
            expect(createUrl('ha.com').toString()).toBe('ha.com');
        });

        test('Ссылка без протокола', () => {
            expect(createUrl('//test.com').toString()).toBe('//test.com/');
        });

        test('Ссылка абсолютная', () => {
            expect(createUrl('/testpage').toString()).toBe('/testpage');
        });

        test('Ссылка c query', () => {
            expect(createUrl('/testpage?test=1').toString()).toBe('/testpage?test=1');
        });
    });
});
