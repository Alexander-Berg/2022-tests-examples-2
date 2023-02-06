describe('home.csp', function () {
    var csp;

    beforeEach(function () {
        csp = new home.CSP();
    });

    describe('normalizeSource', function () {
        it('заменяет относительные пути на \'self\'', function () {
            csp.normalizeSource('style-src', '/path/to/smth?query')
                .should.equal("'self'");

            csp.normalizeSource('style-src', 'path/to/smth?query')
                .should.equal("'self'");
        });

        it('заменяет абсолютные пути на хост', function () {
            csp.normalizeSource('style-src', 'https://host.for/path/to/smth?query')
                .should.equal('host.for');

            csp.normalizeSource('style-src', '//host2.for/path/to/smth?query')
                .should.equal('host2.for');
        });

        it('запрещает data: в скриптах', function () {
            csp.normalizeSource('script-src', 'data:text/javascript,alert("Q!")')
                .should.equal('');
        });

        it('разрешает blob: в скриптах, фреймах и default', function () {
            csp.normalizeSource('script-src', 'blob:QWEQWEQWEQWEQE')
                .should.equal('blob:');

            csp.normalizeSource('child-src', 'blob:QWEQWEQWEQWEQE')
                .should.equal('blob:');

            csp.normalizeSource('default-src', 'blob:QWEQWEQWEQWEQE')
                .should.equal('blob:');
        });


        it('разрешает data: в картинках', function () {
            csp.normalizeSource('img-src', 'data:image/svg+xml,<svg></svg>')
                .should.equal('data:');
        });

        it('не меняет wss:', function () {
            csp.normalizeSource('connect-src', 'wss://xiva.mail/long/path')
                .should.equal('wss://xiva.mail');
        });

        it('разрешает схемы без указания хоста', function () {
            csp.normalizeSource('child-src', 'yandexmaps:')
                .should.equal('yandexmaps:');
        });

        it('запрещает http(s) и ws(s) без хоста', function () {
            csp.normalizeSource('child-src', 'http:')
                .should.equal('');
            csp.normalizeSource('child-src', 'https:')
                .should.equal('');

            csp.normalizeSource('child-src', 'ws:')
                .should.equal('');

            csp.normalizeSource('child-src', 'wss:')
                .should.equal('');
        });
    });
});
