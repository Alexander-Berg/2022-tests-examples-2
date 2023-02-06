const csp = require('../libs/csp');
const config = require('../../etc/config');

describe('Csp', function() {
    var req, res, next;
    beforeEach(function() {
        req = {
            nonce: 'replaced',
            uatraits: {},
            request_id: '23412412423.request.id',
            yandexuid: '12345678',
            mordazone: 'tld',
            get: () => {}
        };
        res = {
            locals: {
                user: {}
            },
            setHeader: (name, value) => {
                if (name !== 'Content-Security-Policy') {
                    throw new TypeError('mock was used not for csp');
                }
                this._value = value;
            }
        };
        next = function() {};
    });

    function parseHeader(header) {
        return header.split(';').reduce((acc, group) => {
            const [directive, ...sources] = group.split(' ');
            acc[directive] = sources;
            return acc;
        }, {});
    }

    it('генерирует правильные заголовки для dev\'а', function() {
        const expectedDirectives = {
            'connect-src': [
                "'self'",
                'yastatic.net',
                'home.yastatic.net',
                'yandex.tld',
                '*.yandex.ru',
                '*.yandex.net',
                'yandex.st',
                'api-maps.yandex.ru',
                'suggest-maps.yandex.ru',
                '*.maps.yandex.net',
                'an.yandex.ru',
                'yandex.ru',
                'mc.admetrica.ru',
                'mc.yandex.tld'
            ],
            'default-src': [
                "'none'"
            ],
            'font-src': [
                'yastatic.net',
                "'self'"
            ],
            'img-src': [
                'data:',
                'yastatic.net',
                '*.maps.yandex.net',
                'api-maps.yandex.ru',
                '*.yandex.net',
                'yandex.ru',
                'yandex.tld',
                'passport.yandex.tld',
                'an.yandex.ru',
                "'self'",
                'mc.admetrica.ru',
                'mc.yandex.ru',
                'mc.yandex.tld',
                '*.mc.yandex.ru'
            ],
            'script-src': [
                "'unsafe-inline'",
                "'unsafe-eval'",
                'yastatic.net',
                'suggest-maps.yandex.tld',
                'api-maps.yandex.ru',
                'social.yandex.tld',
                'yandex.tld',
                '*.maps.yandex.net',
                "'nonce-replaced'",
                "'self'",
                'mc.yandex.ru'
            ],
            'style-src': [
                'blob:',
                "'unsafe-inline'",
                'yastatic.net',
                "'self'"
            ],
            'frame-src': [
                "'self'",
                'api-maps.yandex.ru',
                'pass.yandex.tld',
                'passport.yandex.tld',
                'yandex.tld',
                'morda://*',
                'mc.yandex.ru'
            ],
            'report-uri': [
                'https://csp.yandex.net/csp?from=tune2&project=tune&page=index&showid=23412412423.request.id&yandexuid=12345678'
            ]
        };
        const devflag = config.flags.dev;
        config.flags.dev = true;

        csp(req, res, next);
        const directives = parseHeader(this._value);
        Object.keys(directives).forEach(key => directives[key].should.eql(expectedDirectives[key], key));

        config.flags.dev = devflag;
    });

    it('генерирует правильные заголовки для production\'а', function() {
        const expectedDirectives = {
            'connect-src': [
                "'self'",
                'yastatic.net',
                'home.yastatic.net',
                'yandex.tld',
                '*.yandex.ru',
                '*.yandex.net',
                'yandex.st',
                'api-maps.yandex.ru',
                'suggest-maps.yandex.ru',
                '*.maps.yandex.net',
                'an.yandex.ru',
                'yandex.ru',
                'mc.admetrica.ru',
                'mc.yandex.tld'
            ],
            'default-src': [
                "'none'"
            ],
            'font-src': [
                'yastatic.net'
            ],
            'img-src': [
                'data:',
                'yastatic.net',
                '*.maps.yandex.net',
                'api-maps.yandex.ru',
                '*.yandex.net',
                'yandex.ru',
                'yandex.tld',
                'passport.yandex.tld',
                'an.yandex.ru',
                'mc.admetrica.ru',
                'mc.yandex.ru',
                'mc.yandex.tld',
                '*.mc.yandex.ru'
            ],
            'script-src': [
                "'unsafe-inline'",
                "'unsafe-eval'",
                'yastatic.net',
                'suggest-maps.yandex.tld',
                'api-maps.yandex.ru',
                'social.yandex.tld',
                'yandex.tld',
                '*.maps.yandex.net',
                "'nonce-replaced'",
                'mc.yandex.ru'
            ],
            'style-src': [
                'blob:',
                "'unsafe-inline'",
                'yastatic.net'
            ],
            'frame-src': [
                "'self'",
                'api-maps.yandex.ru',
                'pass.yandex.tld',
                'passport.yandex.tld',
                'yandex.tld',
                'morda://*',
                'mc.yandex.ru'
            ],
            'report-uri': [
                'https://csp.yandex.net/csp?from=tune2&project=tune&page=index&showid=23412412423.request.id&yandexuid=12345678'
            ]
        };

        const devflag = config.flags.dev;
        config.flags.dev = false;

        csp(req, res, next);
        const directives = parseHeader(this._value);
        Object.keys(directives).forEach(key => directives[key].should.eql(expectedDirectives[key], key));

        config.flags.dev = devflag;
    });

    it('оставляет схему для Safari', function() {
        const expectedDirectives = {
            'connect-src': [
                "'self'",
                'https://yastatic.net',
                'https://home.yastatic.net',
                'https://yandex.tld',
                'https://*.yandex.ru',
                'https://*.yandex.net',
                'https://yandex.st',
                'https://api-maps.yandex.ru',
                'https://suggest-maps.yandex.ru',
                'https://*.maps.yandex.net',
                'https://an.yandex.ru',
                'https://yandex.ru',
                'https://mc.admetrica.ru',
                'https://mc.yandex.tld'
            ],
            'default-src': [
                "'none'"
            ],
            'font-src': [
                'https://yastatic.net'
            ],
            'img-src': [
                'data:',
                'https://yastatic.net',
                'https://*.maps.yandex.net',
                'https://api-maps.yandex.ru',
                'https://*.yandex.net',
                'https://yandex.ru',
                'https://yandex.tld',
                'https://passport.yandex.tld',
                'https://an.yandex.ru',
                'https://mc.admetrica.ru',
                'https://mc.yandex.ru',
                'https://mc.yandex.tld',
                'https://*.mc.yandex.ru'
            ],
            'script-src': [
                "'unsafe-inline'",
                "'unsafe-eval'",
                'https://yastatic.net',
                'https://suggest-maps.yandex.tld',
                'https://api-maps.yandex.ru',
                'https://social.yandex.tld',
                'https://yandex.tld',
                'https://*.maps.yandex.net',
                "'nonce-replaced'",
                'https://mc.yandex.ru'
            ],
            'style-src': [
                'blob:',
                "'unsafe-inline'",
                'https://yastatic.net'
            ],
            'frame-src': [
                "'self'",
                'https://api-maps.yandex.ru',
                'https://pass.yandex.tld',
                'https://passport.yandex.tld',
                'https://yandex.tld',
                'morda://*',
                'https://mc.yandex.ru'
            ],
            'report-uri': [
                'https://csp.yandex.net/csp?from=tune2&project=tune&page=index&showid=23412412423.request.id&yandexuid=12345678'
            ]
        };

        const devflag = config.flags.dev;
        config.flags.dev = false;
        req.uatraits = {
            BrowserName: 'Safari'
        };

        csp(req, res, next);
        const directives = parseHeader(this._value);
        Object.keys(directives).forEach(key => directives[key].should.eql(expectedDirectives[key], key));

        config.flags.dev = devflag;
    });

    it('ставит правильные домены для метрики', function() {
        const devflag = config.flags.dev;
        const comConnect = [
            "'self'",
            'yastatic.net',
            'home.yastatic.net',
            'yandex.com',
            '*.yandex.ru',
            '*.yandex.net',
            'yandex.st',
            'api-maps.yandex.ru',
            'suggest-maps.yandex.ru',
            '*.maps.yandex.net',
            'an.yandex.ru',
            'yandex.ru',
            'mc.admetrica.ru',
            'mc.yandex.com'
        ];
        const ruConnect = [
            "'self'",
            'yastatic.net',
            'home.yastatic.net',
            'yandex.ru',
            '*.yandex.ru',
            '*.yandex.net',
            'yandex.st',
            'api-maps.yandex.ru',
            'suggest-maps.yandex.ru',
            '*.maps.yandex.net',
            'an.yandex.ru',
            'mc.admetrica.ru',
            'mc.yandex.ru'
        ];
        const othersConnectFn = tld => [
            "'self'",
            'yastatic.net',
            'home.yastatic.net',
            `yandex.${tld}`,
            '*.yandex.ru',
            '*.yandex.net',
            'yandex.st',
            'api-maps.yandex.ru',
            'suggest-maps.yandex.ru',
            '*.maps.yandex.net',
            'an.yandex.ru',
            'yandex.ru',
            'mc.admetrica.ru',
            `mc.yandex.${tld}`
        ];

        config.flags.dev = false;
        req.mordazone = 'com';
        csp(req, res, next);
        parseHeader(this._value)['connect-src'].should.eql(comConnect, 'com');

        req.mordazone = 'ru';
        csp(req, res, next);
        parseHeader(this._value)['connect-src'].should.eql(ruConnect, 'ru');

        ['by', 'kz', 'ua', 'com.tr'].forEach(function(tld) {
            req.mordazone = tld;
            csp(req, res, next);
            parseHeader(this._value)['connect-src'].should.eql(othersConnectFn(tld), tld);
        }, this);

        config.flags.dev = devflag;
    });

    it('учитывает реферер для метрики при смене tld', function() {
        req.get = () => 'https://yandex.by/tune';
        req.mordazone = 'ru';
        csp(req, res, next);

        const directives = parseHeader(this._value);
        directives['connect-src'].should.to.include('mc.yandex.by');
        directives['img-src'].should.to.include('mc.yandex.by');
        directives['script-src'].should.to.include('mc.yandex.by');

        req.get = () => 'https://yandex.ua/';
        req.mordazone = 'ua';
        csp(req, res, next);
        parseHeader(this._value)['connect-src'].filter(source => source.startsWith('mc.yandex.')).length.should.to.equal(1);
    });

    it('учитывает accept-language для метрики', function () {
        req.langdetect = {
            list: [{id: 'ka'}, {id: 'kk'}]
        };
        req.mordazone = 'ru';
        csp(req, res, next);

        const directives = parseHeader(this._value);
        ['connect-src', 'img-src', 'frame-src'].forEach(name => {
            directives[name].should.to.include('mc.yandex.ge', `${name}: ${directives[name]}`);
            directives[name].should.to.include('mc.yandex.kz', `${name}: ${directives[name]}`);
        });
    });

    it('передаёт правильный page', function () {

        const checkPath = (path, page) => {
            req.path = path;
            csp(req, res, next);

            const directives = parseHeader(this._value);
            directives['report-uri'].should.be.an('array')
                .and.have.lengthOf(1);

            directives['report-uri'][0].should.include('page=' + page, `${path} -> ${page}`);
        };

        checkPath('/', 'index');
        checkPath('/geo', 'geo');
        checkPath('/places', 'places');
        checkPath('/desktop-notifications', 'desktop-notifications');
        checkPath('/desktop-notifications/push', 'desktop-notifications-push');
        checkPath('/desktop-notifications/push/ololo', 'desktop-notifications-push-ololo');
        checkPath('/tune', 'index');
        checkPath('/tune/geo', 'geo');
        checkPath('/tune/places', 'places');
        checkPath('/tune/desktop-notifications', 'desktop-notifications');
        checkPath('/tune/desktop-notifications/push', 'desktop-notifications-push');
        checkPath('/tune/desktop-notifications/push/ololo', 'desktop-notifications-push-ololo');
        checkPath('/tune-rc', 'index');
        checkPath('/tune-rc/geo', 'geo');
        checkPath('/tune-rc/places', 'places');
        checkPath('/tune-rc/desktop-notifications', 'desktop-notifications');
        checkPath('/tune-rc/desktop-notifications/push', 'desktop-notifications-push');
        checkPath('/tune-rc/desktop-notifications/push/ololo', 'desktop-notifications-push-ololo');
    });
});
