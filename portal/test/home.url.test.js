describe('home.parseUrl', function() {
    it('парсит обычный url', function() {
        var url = 'https://ya.ru/test?foo=bar&this%20is=spa%3Drta&equals=bla=bla=bla#zed',
            parsedUrl = home.parseUrl(url);

        parsedUrl.scheme.should.equal('https');
        parsedUrl.host.should.equal('ya.ru');
        parsedUrl.path.should.equal('/test');
        parsedUrl.search.should.equal('foo=bar&this%20is=spa%3Drta&equals=bla=bla=bla');
        parsedUrl.query.should.deep.equal({
            foo: 'bar',
            'this is': 'spa=rta',
            equals: 'bla=bla=bla'
        });
        parsedUrl.hash.should.equal('zed');
    });

    it('парсит обычный url без схемы', function() {
        var url = '//www.ya.ru/test/test1#zed/zed?test',
            parsedUrl = home.parseUrl(url);

        parsedUrl.scheme.should.equal('');
        parsedUrl.host.should.equal('www.ya.ru');
        parsedUrl.path.should.equal('/test/test1');
        parsedUrl.search.should.equal('');
        parsedUrl.query.should.deep.equal({});
        parsedUrl.hash.should.equal('zed/zed?test');
    });

    it('парсит относительный урл от корня', function() {
        var url = '/test/test1?bla',
            parsedUrl = home.parseUrl(url);
        parsedUrl.scheme.should.equal('');
        parsedUrl.host.should.equal('');
        parsedUrl.path.should.equal('/test/test1');
        parsedUrl.search.should.equal('bla');
        parsedUrl.query.should.deep.equal({bla: ''});
        parsedUrl.hash.should.equal('');
    });

    it('парсит относительный урл от текущего пути', function() {
        var url = 'test/test1?bla',
            parsedUrl = home.parseUrl(url);
        parsedUrl.scheme.should.equal('');
        parsedUrl.host.should.equal('');
        parsedUrl.path.should.equal('test/test1');
        parsedUrl.search.should.equal('bla');
        parsedUrl.query.should.deep.equal({bla: ''});
        parsedUrl.hash.should.equal('');
    });

    it('парсит обычный плохой url', function() {
        var url = '/www.y?a.ru/test/test1#zed/zed?test',
            parsedUrl = home.parseUrl(url);

        parsedUrl.scheme.should.equal('');
        parsedUrl.host.should.equal('');
        parsedUrl.path.should.equal('/www.y');
        parsedUrl.search.should.equal('a.ru/test/test1');
        parsedUrl.query.should.deep.equal({
            'a.ru/test/test1': ''
        });
        parsedUrl.hash.should.equal('zed/zed?test');
    });

    it('парсит другой плохой url', function() {
        var url = 'http://ya.ru/?##',
            parsedUrl = home.parseUrl(url);

        parsedUrl.scheme.should.equal('http');
        parsedUrl.host.should.equal('ya.ru');
        parsedUrl.path.should.equal('');
        parsedUrl.search.should.equal('');
        parsedUrl.query.should.deep.equal({});
        parsedUrl.hash.should.equal('');
    });

    it('парсит url из одного хоста', function() {
        var url = '//ya.ru',
            parsedUrl = home.parseUrl(url);

        parsedUrl.scheme.should.equal('');
        parsedUrl.host.should.equal('ya.ru');
        parsedUrl.path.should.equal('');
        parsedUrl.search.should.equal('');
        parsedUrl.hash.should.equal('');
    });

    it('парсит недоэнкоженный урл', function() {
        // encodeURIComponent('Магазины') + ' сейчас'
        var url = 'http://ya.ru?text=%D0%9C%D0%B0%D0%B3%D0%B0%D0%B7%D0%B8%D0%BD%D1%8B сейчас',
            parsedUrl = home.parseUrl(url);

        parsedUrl.scheme.should.equal('http');
        parsedUrl.host.should.equal('ya.ru');
        parsedUrl.path.should.equal('');
        parsedUrl.search.should.equal('text=%D0%9C%D0%B0%D0%B3%D0%B0%D0%B7%D0%B8%D0%BD%D1%8B сейчас');
        parsedUrl.query.should.deep.equal({text: 'Магазины сейчас'});
        parsedUrl.hash.should.equal('');
    });

    it('парсит урл с одинаковыми параметрами', function() {
        var url = 'https://www.yandex.com.tr/suggest/suggest-ya.cgi?srv=serp_com_tr_desktop&' +
            'html=1&mob=0&portal=1&platform=desktop&show_experiment=222&show_experiment=224',
            parsedUrl = home.parseUrl(url);

        parsedUrl.should.deep.equal({
            hash: '',
            host: 'www.yandex.com.tr',
            path: '/suggest/suggest-ya.cgi',
            query: {
                'srv': 'serp_com_tr_desktop',
                'html': '1',
                'mob': '0',
                'portal': '1',
                'platform': 'desktop',
                'show_experiment': '224'
            },
            scheme: 'https',
            search: 'srv=serp_com_tr_desktop&html=1&mob=0&portal=1&platform=desktop&show_experiment=222&show_experiment=224'
        });

        parsedUrl = home.parseUrl(url, {multi: true});

        parsedUrl.should.deep.equal({
            hash: '',
            host: 'www.yandex.com.tr',
            path: '/suggest/suggest-ya.cgi',
            query: {
                'srv': 'serp_com_tr_desktop',
                'html': '1',
                'mob': '0',
                'portal': '1',
                'platform': 'desktop',
                'show_experiment': ['222', '224']
            },
            scheme: 'https',
            search: 'srv=serp_com_tr_desktop&html=1&mob=0&portal=1&platform=desktop&show_experiment=222&show_experiment=224'
        });
    });
});

describe('home.makeUrl', function() {
    it('собирает относительные урлы', function() {
        home.makeUrl({
            path: 'path/to/smth',
            query: {bla: 4}
        }).should.equal('path/to/smth?bla=4');

        home.makeUrl({
            path: '/path/to/smth',
            query: {bla: 4}
        }).should.equal('/path/to/smth?bla=4');
    });

    it('собирает абсолютные урлы', function() {
        home.makeUrl({
            host: 'ya.ru'
        }).should.equal('//ya.ru/');

        home.makeUrl({
            scheme: 'http',
            host: 'ya.ru'
        }).should.equal('http://ya.ru/');

        home.makeUrl({
            host: 'ya.ru',
            path: 'path/to/smth',
            query: {bla: 4}
        }).should.equal('//ya.ru/path/to/smth?bla=4');

        home.makeUrl({
            host: 'ya.ru',
            path: '/path/to/smth',
            query: {bla: 4}
        }).should.equal('//ya.ru/path/to/smth?bla=4');

        home.makeUrl({
            scheme: 'ftp',
            host: 'ya.ru',
            path: '/path/to/smth',
            query: {bla: 4}
        }).should.equal('ftp://ya.ru/path/to/smth?bla=4');
    });

    it('собирает параметры', function() {
        home.makeUrl({
            query: {bla: 4}
        }).should.equal('?bla=4');

        home.makeUrl({
            query: {foo: 4, bar: false, baz: ''}
        }).should.equal('?foo=4&bar=false&baz');

        home.makeUrl({
            query: {'?=': '='}
        }).should.equal('?%3F%3D=%3D');
    });

    it('добавляет хэш', function() {
        home.makeUrl({
            path: '/path/to',
            hash: 'smth'
        }).should.equal('/path/to#smth');
        home.makeUrl({
            host: 'ya.ru',
            hash: 'smth'
        }).should.equal('//ya.ru/#smth');
    });

    it('не добавляет схему без хоста', function() {
        home.makeUrl({
            scheme: 'https',
            path: '/path/to',
            hash: 'smth'
        }).should.equal('/path/to#smth');
    });

    it('генерирует интентные ссылки', function() {
        home.makeUrl({
            scheme: 'yandexmaps',
            query: {
                l: 'trf',
                z: '10'
            }
        }).should.equal('yandexmaps://?l=trf&z=10');

        home.makeUrl({
            scheme: 'intent',
            host: 'maps.yandex.ru',
            query: {
                l: 'trf',
                z: '10'
            }
        }).should.equal('intent://maps.yandex.ru/?l=trf&z=10');
    });

    it('генерирует query с массивом', function() {
        home.makeUrl({
            host: 'ya.ru',
            path: '/path/to/smth',
            query: {bla: [4, '5']}
        }).should.equal('//ya.ru/path/to/smth?bla=4&bla=5');
    });

    it('генерирует query с null', function() {
        home.makeUrl({
            host: 'ya.ru',
            path: '/path/to/smth',
            query: {bla: null}
        }).should.equal('//ya.ru/path/to/smth');

        home.makeUrl({
            host: 'ya.ru',
            path: '/path/to/smth',
            query: {bla: null, asd: 123}
        }).should.equal('//ya.ru/path/to/smth?asd=123');
    });
});

describe('addQueryToUrl', function () {
    describe('добавляет новые параметры', function () {
        it('в пустой урл', function () {
            home.addQueryToUrl('', {x: 5})
                .should.equal('?x=5');
        });

        it('в query урл', function () {
            home.addQueryToUrl('?a', {x: 5})
                .should.equal('?a&x=5');
        });

        it('в относительный урл', function () {
            home.addQueryToUrl('relpath', {x: 5})
                .should.equal('relpath?x=5');

            home.addQueryToUrl('rel/path', {x: 5})
                .should.equal('rel/path?x=5');
        });

        it('в абсолютный урл без хоста', function () {
            home.addQueryToUrl('/abspath', {x: 5})
                .should.equal('/abspath?x=5');

            home.addQueryToUrl('/abs/path', {x: 5})
                .should.equal('/abs/path?x=5');
        });

        it('в абсолютный урл c хостом без схемы', function () {
            home.addQueryToUrl('//ya.ru/abspath', {x: 5})
                .should.equal('//ya.ru/abspath?x=5');

            home.addQueryToUrl('//ya.ru/abs/path', {x: 5})
                .should.equal('//ya.ru/abs/path?x=5');
        });

        it('в абсолютный урл c хостом со схемой', function () {
            home.addQueryToUrl('https://ya.ru/abspath', {x: 5})
                .should.equal('https://ya.ru/abspath?x=5');

            home.addQueryToUrl('https://ya.ru/abs/path', {x: 5})
                .should.equal('https://ya.ru/abs/path?x=5');
        });

        it('урл c хешем', function () {
            home.addQueryToUrl('relpath#nofranky', {x: 5})
                .should.equal('relpath?x=5#nofranky');

            home.addQueryToUrl('rel/path#nofranky', {x: 5})
                .should.equal('rel/path?x=5#nofranky');

            home.addQueryToUrl('/abs/path#nofranky', {x: 5})
                .should.equal('/abs/path?x=5#nofranky');

            home.addQueryToUrl('//ya.ru/abs/path#nofranky', {x: 5})
                .should.equal('//ya.ru/abs/path?x=5#nofranky');

            home.addQueryToUrl('https://ya.ru/abs/path#nofranky', {x: 5})
                .should.equal('https://ya.ru/abs/path?x=5#nofranky');
        });
    });

    describe('заменяет параметры', function () {
        it('в query урл', function () {
            home.addQueryToUrl('?a&x=2', {x: 5})
                .should.equal('?a&x=5');
        });

        it('в относительный урл', function () {
            home.addQueryToUrl('relpath?x=2', {x: 5})
                .should.equal('relpath?x=5');

            home.addQueryToUrl('rel/path?x=2', {x: 5})
                .should.equal('rel/path?x=5');
        });

        it('в абсолютный урл без хоста', function () {
            home.addQueryToUrl('/abspath?x=2', {x: 5})
                .should.equal('/abspath?x=5');

            home.addQueryToUrl('/abs/path?x=2', {x: 5})
                .should.equal('/abs/path?x=5');
        });

        it('в абсолютный урл c хостом без схемы', function () {
            home.addQueryToUrl('//ya.ru/abspath?x=2', {x: 5})
                .should.equal('//ya.ru/abspath?x=5');

            home.addQueryToUrl('//ya.ru/abs/path?x=2', {x: 5})
                .should.equal('//ya.ru/abs/path?x=5');
        });

        it('в абсолютный урл c хостом со схемой', function () {
            home.addQueryToUrl('https://ya.ru/abspath?x=2', {x: 5})
                .should.equal('https://ya.ru/abspath?x=5');

            home.addQueryToUrl('https://ya.ru/abs/path?x=2', {x: 5})
                .should.equal('https://ya.ru/abs/path?x=5');
        });

        it('урл c хешем', function () {
            home.addQueryToUrl('relpath?x=2&a&b=x#nofranky', {x: 5})
                .should.equal('relpath?x=5&a&b=x#nofranky');

            home.addQueryToUrl('rel/path?x=2&a&b=x#nofranky', {x: 5})
                .should.equal('rel/path?x=5&a&b=x#nofranky');

            home.addQueryToUrl('/abs/path?x=2&a&b=x#nofranky', {x: 5})
                .should.equal('/abs/path?x=5&a&b=x#nofranky');

            home.addQueryToUrl('//ya.ru/abs/path?x=2&a&b=x#nofranky', {x: 5})
                .should.equal('//ya.ru/abs/path?x=5&a&b=x#nofranky');

            home.addQueryToUrl('https://ya.ru/abs/path?x=2&a&b=x#nofranky', {x: 5})
                .should.equal('https://ya.ru/abs/path?x=5&a&b=x#nofranky');
        });
    });

});

describe('home.parseSearch', function() {
    it('выкидывает кривые параметры', function() {
        var search = 'foo=bar&bad=va%%lue',
            query = home.parseSearch(search);

        query.should.deep.equal({
            foo: 'bar'
        });
    });
});
