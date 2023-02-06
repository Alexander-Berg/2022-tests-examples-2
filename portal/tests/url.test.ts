import { logError } from '@lib/log/logError';
import { parseSearch, parseUrl, makeUrl, addQueryToUrl } from '../url';

jest.mock('../../log/logError.ts', () => {
    return {
        logError: jest.fn().mockImplementation(() => {
            throw new Error('logError called!');
        })
    };
});
const mockedLogError = logError as jest.Mock;

describe('parseUrl', function() {
    test('парсит обычный url', function() {
        let url = 'https://ya.ru/test?foo=bar&this%20is=spa%3Drta&equals=bla=bla=bla#zed';
        let parsedUrl = parseUrl(url);

        expect(parsedUrl).toEqual({
            scheme: 'https',
            host: 'ya.ru',
            path: '/test',
            search: 'foo=bar&this%20is=spa%3Drta&equals=bla=bla=bla',
            query: {
                foo: 'bar',
                'this is': 'spa=rta',
                equals: 'bla=bla=bla'
            },
            hash: 'zed'
        });
    });

    test('парсит обычный url без схемы', function() {
        let url = '//www.ya.ru/test/test1#zed/zed?test';
        let parsedUrl = parseUrl(url);

        expect(parsedUrl).toEqual({
            scheme: '',
            host: 'www.ya.ru',
            path: '/test/test1',
            search: '',
            query: {},
            hash: 'zed/zed?test'
        });
    });

    test('парсит относительный урл от корня', function() {
        let url = '/test/test1?bla';
        let parsedUrl = parseUrl(url);

        expect(parsedUrl).toEqual({
            scheme: '',
            host: '',
            path: '/test/test1',
            search: 'bla',
            query: { bla: '' },
            hash: ''
        });
    });

    test('парсит относительный урл от текущего пути', function() {
        let url = 'test/test1?bla';
        let parsedUrl = parseUrl(url);

        expect(parsedUrl).toEqual({
            scheme: '',
            host: '',
            path: 'test/test1',
            search: 'bla',
            query: { bla: '' },
            hash: ''
        });
    });

    test('парсит обычный плохой url', function() {
        let url = '/www.y?a.ru/test/test1#zed/zed?test';
        let parsedUrl = parseUrl(url);

        expect(parsedUrl).toEqual({
            scheme: '',
            host: '',
            path: '/www.y',
            search: 'a.ru/test/test1',
            query: {
                'a.ru/test/test1': ''
            },
            hash: 'zed/zed?test'
        });
    });

    test('парсит другой плохой url', function() {
        let url = 'http://ya.ru/?##';
        let parsedUrl = parseUrl(url);

        expect(parsedUrl).toEqual({
            scheme: 'http',
            host: 'ya.ru',
            path: '',
            search: '',
            query: {},
            hash: ''
        });
    });

    test('парсит url из одного хоста', function() {
        let url = '//ya.ru';
        let parsedUrl = parseUrl(url);

        expect(parsedUrl).toEqual({
            scheme: '',
            host: 'ya.ru',
            path: '',
            search: '',
            hash: '',
            query: {}
        });
    });

    test('парсит недоэнкоженный урл', function() {
        // encodeURIComponent('Магазины') + ' сейчас'
        let url = 'http://ya.ru?text=%D0%9C%D0%B0%D0%B3%D0%B0%D0%B7%D0%B8%D0%BD%D1%8B сейчас';
        let parsedUrl = parseUrl(url);

        expect(parsedUrl).toEqual({
            scheme: 'http',
            host: 'ya.ru',
            path: '',
            search: 'text=%D0%9C%D0%B0%D0%B3%D0%B0%D0%B7%D0%B8%D0%BD%D1%8B сейчас',
            query: { text: 'Магазины сейчас' },
            hash: ''
        });
    });

    test('парсит урл с одинаковыми параметрами', function() {
        let url = 'https://www.yandex.com.tr/suggest/suggest-ya.cgi?srv=serp_com_tr_desktop&' +
            'html=1&mob=0&portal=1&platform=desktop&show_experiment=222&show_experiment=224';
        let parsedUrl = parseUrl(url);

        expect(parsedUrl).toEqual({
            hash: '',
            host: 'www.yandex.com.tr',
            path: '/suggest/suggest-ya.cgi',
            query: {
                srv: 'serp_com_tr_desktop',
                html: '1',
                mob: '0',
                portal: '1',
                platform: 'desktop',
                show_experiment: '224'
            },
            scheme: 'https',
            search: 'srv=serp_com_tr_desktop&html=1&mob=0&portal=1&platform=desktop&show_experiment=222&show_experiment=224'
        });

        parsedUrl = parseUrl(url, { multi: true });

        expect(parsedUrl).toEqual({
            hash: '',
            host: 'www.yandex.com.tr',
            path: '/suggest/suggest-ya.cgi',
            query: {
                srv: 'serp_com_tr_desktop',
                html: '1',
                mob: '0',
                portal: '1',
                platform: 'desktop',
                show_experiment: ['222', '224']
            },
            scheme: 'https',
            search: 'srv=serp_com_tr_desktop&html=1&mob=0&portal=1&platform=desktop&show_experiment=222&show_experiment=224'
        });
    });
});

describe('makeUrl', function() {
    test('собирает относительные урлы', function() {
        expect(makeUrl({
            path: 'path/to/smth',
            query: { bla: 4 }
        })).toEqual('path/to/smth?bla=4');

        expect(makeUrl({
            path: '/path/to/smth',
            query: { bla: 4 }
        })).toEqual('/path/to/smth?bla=4');
    });

    test('собирает абсолютные урлы', function() {
        expect(makeUrl({
            host: 'ya.ru'
        })).toEqual('//ya.ru/');

        expect(makeUrl({
            scheme: 'http',
            host: 'ya.ru'
        })).toEqual('http://ya.ru/');

        expect(makeUrl({
            host: 'ya.ru',
            path: 'path/to/smth',
            query: { bla: 4 }
        })).toEqual('//ya.ru/path/to/smth?bla=4');

        expect(makeUrl({
            host: 'ya.ru',
            path: '/path/to/smth',
            query: { bla: 4 }
        })).toEqual('//ya.ru/path/to/smth?bla=4');

        expect(makeUrl({
            scheme: 'ftp',
            host: 'ya.ru',
            path: '/path/to/smth',
            query: { bla: 4 }
        })).toEqual('ftp://ya.ru/path/to/smth?bla=4');
    });

    test('собирает параметры', function() {
        expect(makeUrl({
            query: { bla: 4 }
        })).toEqual('?bla=4');

        expect(makeUrl({
            query: { foo: 4, bar: false, baz: '' }
        })).toEqual('?foo=4&bar=false&baz');

        expect(makeUrl({
            query: { '?=': '=' }
        })).toEqual('?%3F%3D=%3D');
    });

    test('добавляет хэш', function() {
        expect(makeUrl({
            path: '/path/to',
            hash: 'smth'
        })).toEqual('/path/to#smth');
        expect(makeUrl({
            host: 'ya.ru',
            hash: 'smth'
        })).toEqual('//ya.ru/#smth');
    });

    test('не добавляет схему без хоста', function() {
        expect(makeUrl({
            scheme: 'https',
            path: '/path/to',
            hash: 'smth'
        })).toEqual('/path/to#smth');
    });

    test('генерирует интентные ссылки', function() {
        expect(makeUrl({
            scheme: 'yandexmaps',
            query: {
                l: 'trf',
                z: '10'
            }
        })).toEqual('yandexmaps://?l=trf&z=10');

        expect(makeUrl({
            scheme: 'intent',
            host: 'maps.yandex.ru',
            query: {
                l: 'trf',
                z: '10'
            }
        })).toEqual('intent://maps.yandex.ru/?l=trf&z=10');
    });

    test('генерирует query с массивом', function() {
        expect(makeUrl({
            host: 'ya.ru',
            path: '/path/to/smth',
            query: { bla: [4, '5'] }
        })).toEqual('//ya.ru/path/to/smth?bla=4&bla=5');
    });

    test('генерирует query с null', function() {
        expect(makeUrl({
            host: 'ya.ru',
            path: '/path/to/smth',
            query: { bla: null }
        })).toEqual('//ya.ru/path/to/smth');

        expect(makeUrl({
            host: 'ya.ru',
            path: '/path/to/smth',
            query: { bla: null, asd: 123 }
        })).toEqual('//ya.ru/path/to/smth?asd=123');
    });
});

describe('addQueryToUrl', function() {
    describe('добавляет новые параметры', function() {
        test('в пустой урл', function() {
            expect(addQueryToUrl('', { x: 5 }))
                .toEqual('?x=5');
        });

        test('в query урл', function() {
            expect(addQueryToUrl('?a', { x: 5 }))
                .toEqual('?a&x=5');
        });

        test('в относительный урл', function() {
            expect(addQueryToUrl('relpath', { x: 5 }))
                .toEqual('relpath?x=5');

            expect(addQueryToUrl('rel/path', { x: 5 }))
                .toEqual('rel/path?x=5');
        });

        test('в абсолютный урл без хоста', function() {
            expect(addQueryToUrl('/abspath', { x: 5 }))
                .toEqual('/abspath?x=5');

            expect(addQueryToUrl('/abs/path', { x: 5 }))
                .toEqual('/abs/path?x=5');
        });

        test('в абсолютный урл c хостом без схемы', function() {
            expect(addQueryToUrl('//ya.ru/abspath', { x: 5 }))
                .toEqual('//ya.ru/abspath?x=5');

            expect(addQueryToUrl('//ya.ru/abs/path', { x: 5 }))
                .toEqual('//ya.ru/abs/path?x=5');
        });

        test('в абсолютный урл c хостом со схемой', function() {
            expect(addQueryToUrl('https://ya.ru/abspath', { x: 5 }))
                .toEqual('https://ya.ru/abspath?x=5');

            expect(addQueryToUrl('https://ya.ru/abs/path', { x: 5 }))
                .toEqual('https://ya.ru/abs/path?x=5');
        });

        test('урл c хешем', function() {
            expect(addQueryToUrl('relpath#nofranky', { x: 5 }))
                .toEqual('relpath?x=5#nofranky');

            expect(addQueryToUrl('rel/path#nofranky', { x: 5 }))
                .toEqual('rel/path?x=5#nofranky');

            expect(addQueryToUrl('/abs/path#nofranky', { x: 5 }))
                .toEqual('/abs/path?x=5#nofranky');

            expect(addQueryToUrl('//ya.ru/abs/path#nofranky', { x: 5 }))
                .toEqual('//ya.ru/abs/path?x=5#nofranky');

            expect(addQueryToUrl('https://ya.ru/abs/path#nofranky', { x: 5 }))
                .toEqual('https://ya.ru/abs/path?x=5#nofranky');
        });
    });

    describe('заменяет параметры', function() {
        test('в query урл', function() {
            expect(addQueryToUrl('?a&x=2', { x: 5 }))
                .toEqual('?a&x=5');
        });

        test('в относительный урл', function() {
            expect(addQueryToUrl('relpath?x=2', { x: 5 }))
                .toEqual('relpath?x=5');

            expect(addQueryToUrl('rel/path?x=2', { x: 5 }))
                .toEqual('rel/path?x=5');
        });

        test('в абсолютный урл без хоста', function() {
            expect(addQueryToUrl('/abspath?x=2', { x: 5 }))
                .toEqual('/abspath?x=5');

            expect(addQueryToUrl('/abs/path?x=2', { x: 5 }))
                .toEqual('/abs/path?x=5');
        });

        test('в абсолютный урл c хостом без схемы', function() {
            expect(addQueryToUrl('//ya.ru/abspath?x=2', { x: 5 }))
                .toEqual('//ya.ru/abspath?x=5');

            expect(addQueryToUrl('//ya.ru/abs/path?x=2', { x: 5 }))
                .toEqual('//ya.ru/abs/path?x=5');
        });

        test('в абсолютный урл c хостом со схемой', function() {
            expect(addQueryToUrl('https://ya.ru/abspath?x=2', { x: 5 }))
                .toEqual('https://ya.ru/abspath?x=5');

            expect(addQueryToUrl('https://ya.ru/abs/path?x=2', { x: 5 }))
                .toEqual('https://ya.ru/abs/path?x=5');
        });

        test('урл c хешем', function() {
            expect(addQueryToUrl('relpath?x=2&a&b=x#nofranky', { x: 5 }))
                .toEqual('relpath?x=5&a&b=x#nofranky');

            expect(addQueryToUrl('rel/path?x=2&a&b=x#nofranky', { x: 5 }))
                .toEqual('rel/path?x=5&a&b=x#nofranky');

            expect(addQueryToUrl('/abs/path?x=2&a&b=x#nofranky', { x: 5 }))
                .toEqual('/abs/path?x=5&a&b=x#nofranky');

            expect(addQueryToUrl('//ya.ru/abs/path?x=2&a&b=x#nofranky', { x: 5 }))
                .toEqual('//ya.ru/abs/path?x=5&a&b=x#nofranky');

            expect(addQueryToUrl('https://ya.ru/abs/path?x=2&a&b=x#nofranky', { x: 5 }))
                .toEqual('https://ya.ru/abs/path?x=5&a&b=x#nofranky');
        });
    });
});

describe('parseSearch', function() {
    afterEach(() => {
        jest.clearAllMocks();
    });

    test('выкидывает кривые параметры', function() {
        mockedLogError.mockImplementation(() => {});

        let search = 'foo=bar&bad=va%%lue';
        let query = parseSearch(search);

        expect(query).toEqual({
            foo: 'bar'
        });

        expect(mockedLogError.mock.calls).toEqual([[{
            block: 'url',
            message: 'parseSearch: URI malformed; token: bad=va%%lue'
        }]]);
    });
});
