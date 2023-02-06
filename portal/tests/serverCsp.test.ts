import { CSP } from '../serverCsp';

describe('home.csp', function() {
    let csp: CSP;

    beforeEach(function() {
        csp = new CSP();
    });

    describe('normalizeSource', function() {
        test('заменяет относительные пути на \'self\'', function() {
            expect(csp.normalizeSource('style-src', '/path/to/smth?query'))
                .toEqual("'self'");

            expect(csp.normalizeSource('style-src', 'path/to/smth?query'))
                .toEqual("'self'");
        });

        test('заменяет абсолютные пути на хост', function() {
            expect(csp.normalizeSource('style-src', 'https://host.for/path/to/smth?query'))
                .toEqual('host.for');

            expect(csp.normalizeSource('style-src', '//host2.for/path/to/smth?query'))
                .toEqual('host2.for');
        });

        test('запрещает data: в скриптах', function() {
            expect(csp.normalizeSource('script-src', 'data:text/javascript,alert("Q!")'))
                .toEqual('');
        });

        test('разрешает blob: в скриптах, фреймах и default', function() {
            expect(csp.normalizeSource('script-src', 'blob:QWEQWEQWEQWEQE'))
                .toEqual('blob:');

            expect(csp.normalizeSource('child-src', 'blob:QWEQWEQWEQWEQE'))
                .toEqual('blob:');

            expect(csp.normalizeSource('default-src', 'blob:QWEQWEQWEQWEQE'))
                .toEqual('blob:');
        });

        test('разрешает data: в картинках', function() {
            expect(csp.normalizeSource('img-src', 'data:image/svg+xml,<svg></svg>'))
                .toEqual('data:');
        });

        test('не меняет wss:', function() {
            expect(csp.normalizeSource('connect-src', 'wss://xiva.mail/long/path'))
                .toEqual('wss://xiva.mail');
        });

        test('разрешает схемы без указания хоста', function() {
            expect(csp.normalizeSource('child-src', 'yandexmaps:'))
                .toEqual('yandexmaps:');
        });

        test('запрещает http(s) и ws(s) без хоста', function() {
            expect(csp.normalizeSource('child-src', 'http:'))
                .toEqual('');
            expect(csp.normalizeSource('child-src', 'https:'))
                .toEqual('');

            expect(csp.normalizeSource('child-src', 'ws:'))
                .toEqual('');

            expect(csp.normalizeSource('child-src', 'wss:'))
                .toEqual('');
        });
    });
});
