const check = require('../libs/check_retpath');

describe('Check Retpath', function() {
    beforeEach(function() {
        this._req = {
            query: {},
            mordazone: 'tld'
        };
        this._next = function() {};
    });
    it('ничего не делает с "нашими" урлами', function() {
        var ours = [
            '//yandex.ru',
            'http://yandex.ru',
            'https://yandex.ru',
            '//ya.ru',
            '//mail.yandex.ru',
            '//long.sequence.of.subdomains.yandex.ru',
            '//yandex.com',
            '//yandex.com.tr',
            '//yandex.ua',
            '//yandex.kz',
            '//yandex.by',
            '//yandex.ru/path/to/the/page',
            '//yandex.ru/?query=arg&and=encoded%20arg&retpath=%2F%2Fevil.com'
        ];
        ours.forEach(url => {
            this._req.retpath = '';
            this._req.query.retpath = url;
            check(this._req, {}, this._next);
            this._req.retpath.should.equal(url.replace(/^(http:)?\/\//, 'https://'));
        });
    });
    
    it('оборачивает в clck "чужие" урлы', function() {
        var stranger = [
            '//evil.com',
            'http://evil.com',
            'https://evil.com',
            '//evilyandex.ru',
            '//ya.com',
            '//ya.com.tr',
            '//ya.by',
            '//ya.kz',
            '//ya.ua',
            '//yandex.evil.com',
            '//yandex.ru.evil.com',
            '//ya.ru.evil.com',
            '//evil.com/yandex.ru',
            '//evil.com//yandex.ru',
            '//evil.com/ya.ru',
            '//evil.com//ya.ru',
            '//evil.com/path/to/smth/yandex.ru',
            '//evil.com/path/to/smth//yandex.ru',
            '//evil.com/path/to/smth/ya.ru',
            '//evil.com/path/to/smth//ya.ru',
            '//evil.com/?arg=//yandex.ru',
            '//evil.com/?arg=%2F%2Fyandex.ru',
            '//evil.com/?arg=//ya.ru',
            '//evil.com/?arg=%2F%2Fya.ru',
            'https://www.yandex.ru:12@www.buglloc.com',
            'https://www.yandex.ru_.www.buglloc.com',
            'http://www.buglloc.com%2dyandex.ru',
            '/\/www.buglloc.com',
            '/\t/www.buglloc.com',
            '//www.buglloc.com',
            '/relative/url'
        ];
        stranger.forEach(url => {
            this._req.retpath = '';
            this._req.query.retpath = url;
            check(this._req, {}, this._next);
            this._req.retpath.should.equal('https://yandex.tld/clck/redir/*data=url=' + encodeURIComponent(url));
        });
    });
});