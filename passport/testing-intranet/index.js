const common = require('../common');
const url = require('url');
const _ = require('lodash');
const CSP = common.CSP;

exports.version = '{{VERSION}}';
exports.defaults = {
    url: {
        protocol: 'http',
        hostname: '127.0.0.1',
        port: '6000',
        pathname: '/1/'
    },
    headers: {
        'content-type': 'application/x-www-form-urlencoded',
        'User-Agent': 'got'
    },
    qs: {
        consumer: 'passport'
    },
    method: 'POST',
    timeout: 10000
};

exports.api = {
    yasms: {
        dao: {
            maxRetries: 5,
            maxConnections: 100,
            retryAfter: 100, // Milliseconds to wait before retrying
            retryCodes: ['INTERROR'],
            timeout: 8000
        }
    },
    oauth: {
        dao: {
            baseUrl: 'http://oauth-test-internal.yandex-team.ru/iface_api',
            maxRetries: 3,
            maxConnections: 100,
            retryAfter: 500, // Milliseconds to wait before retrying
            retryCodes: ['backend.failed'],
            timeout: 1000
        }
    },
    passport: {
        dao: {
            baseUrl: url.format(_.assign({}, exports.defaults.url, {pathname: null})),
            maxRetries: 1,
            maxConnections: 100,
            retryAfter: 300, // Milliseconds to wait before retrying
            retryCodes: ['blackboxfailed'],
            timeout: exports.defaults.timeout
        }
    },
    disk: {
        dao: {
            baseUrl: 'http://sync.disk.yandex.net:8090',
            maxRetries: 3,
            maxConnections: 100,
            retryAfter: 500, // Milliseconds to wait before retrying
            timeout: 1000
        }
    },
    cloud: {
        dao: {
            baseUrl: 'http://intapi.disk.yandex.net:8080',
            maxRetries: 5,
            maxConnections: 100,
            retryAfter: 100, // Milliseconds to wait before retrying
            timeout: 8000
        }
    },
    connect: {
        dao: {
            baseUrl: 'https://api.test.directory.yandex.ru',
            maxRetries: 1,
            maxConnections: 100,
            retryAfter: 100, // Milliseconds to wait before retrying
            timeout: 8000
        }
    },
    geo: {
        dao: {
            baseUrl: 'http://addrs-testing.search.yandex.net/search/stable',
            maxRetries: 1,
            maxConnections: 100,
            retryAfter: 100, // Milliseconds to wait before retrying
            timeout: 8000
        }
    },
    afisha: {
        dao: {
            baseUrl: 'https://api.draqla.afisha.tst.yandex.net',
            maxRetries: 5,
            maxConnections: 100,
            retryAfter: 100, // Milliseconds to wait before retrying
            timeout: 8000
        }
    },
    iot: {
        dao: {
            baseUrl: 'http://quasar-iot-dev-copy-mavlyutov-1.sas.yp-c.yandex.net:8080',
            maxRetries: 5,
            maxConnections: 100,
            retryAfter: 100, // Milliseconds to wait before retrying
            timeout: 8000
        }
    },
    kinopoisk: {
        dao: {
            baseUrl: 'https://api-testing.ott.yandex.ru:443',
            maxRetries: 5,
            maxConnections: 100,
            retryAfter: 100, // Milliseconds to wait before retrying
            timeout: 8000
        }
    },
    billingInternal: {
        dao: {
            baseUrl: 'http://api.mt.mediabilling.yandex.net:80/',
            maxRetries: 5,
            maxConnections: 100,
            retryAfter: 100, // Milliseconds to wait before retrying
            timeout: 8000
        }
    },
    plusLanding: {
        dao: {
            baseUrl: 'https://landing.tst.plus.yandex.net:443/',
            maxRetries: 5,
            maxConnections: 100,
            retryAfter: 100, // Milliseconds to wait before retrying
            timeout: 8000
        }
    },
    trustPayments: {
        dao: {
            token: 'passport_d056025fbea3c4700729c5b96b0ff97b',
            baseUrl: 'https://trust-payments-test.paysys.yandex.net:8028/trust-payments',
            maxRetries: 5,
            maxConnections: 100,
            retryAfter: 100,
            timeout: 8000
        }
    },
    trustApi: {
        dao: {
            baseUrl: 'https://api.trust.test.yandex.net',
            maxRetries: 1,
            maxConnections: 100,
            retryAfter: 100,
            timeout: 200
        }
    },
    praktikum: {
        dao: {
            baseUrl: 'https://testing.pierce.praktikum.yandex-team.ru',
            maxRetries: 5,
            maxConnections: 100,
            retryAfter: 100, // Milliseconds to wait before retrying
            timeout: 8000
        }
    },
    deleteData: {
        baseUrls: common.deleteDataTestingBaseUrls,
        dao: {
            maxRetries: 0,
            maxConnections: 100,
            retryAfter: 0, // Milliseconds to wait before retrying
            timeout: 1000
        }
    }
};

exports.langs = ['ru', 'uk', 'en', 'tr', 'id', 'fr', 'fi'];

exports.paths = {
    retpath: '/passport?mode=passport',
    basic: '/registration',
    static: '{{STATIC_PATH}}',
    blackbox: 'blackbox-test.yandex-team.ru',
    mda: 'pass-test.yandex-team.ru',
    social_static: common.socialStatic,
    providers: 'http://social.yandex.ru/providers-domik.json',
    broker: 'https://social.yandex.%tld%/broker2/start',
    oauth: 'oauth-test.yandex-team.%tld%',
    internal: 'passport-test-internal.yandex-team.ru',
    internalPort: '81',
    experiments: 'http://uaas.search.yandex.net/passport',
    avatar: {
        host: 'center.yandex-team.ru',
        pathname: '/api/v1/user/%login%/avatar/%size%.jpg'
    },
    ysa: {
        static: 'https://ysa-test-static.passport.yandex.net',
        hostname: 'ysa-test.passport.yandex.net',
        port: '80'
    },
    yasms: 'http://sms.passport.yandex.ru',
    unread: {
        host: 'export.yandex.%tld%',
        pathname: '/for/unread.xml'
    },
    loginStatusPath: '/auth/login-status.html',
    bigbro: {
        hostname: 'karma.yandex.net',
        port: '80'
    },
    help: {
        passport: 'https://wiki.yandex-team.ru/passport/'
    },
    logs: {
        graphite: '/var/log/yandex/passport-frontend/graphite.log',
        requests: '/var/log/yandex/passport-frontend/requests.log'
    },
    emailValidator: '//passport-test.yandex-team.%tld%/profile/emails/',
    embeddedauth: '//passport-test.yandex-team.%tld%/passport?mode=embeddedauth',
    yamoney: null,
    mapsAPI: 'https://api-maps.yandex.ru/2.1/?lang=%lang%',
    yamoneyCards: 'https://money.yandex.%tld%/cards',
    tunePlaces: common.tunePlaces,
    marketAddresses: common.marketAddresses,
    staticMaps: common.staticMaps,
    authCustomsStatic: 'https://yastatic.net/s3/passport-auth-customs/',
    accountsUrl: '//api.passport-test.yandex.%tld%/all_accounts',
    yaPayLanding: common.yaPayLanding
};

exports.intranetPaths = {
    retpath: '/passport?mode=passport',
    blackbox: 'blackbox-test.yandex-team.ru',
    mda: 'pass-test.yandex-team.ru'
};

exports.brokerParams = {
    startUrl: '/auth/social/start',
    retpath: '/auth/i-social__closer.html',
    consumer: 'passport',
    popupName: 'passport_social',
    display: 'popup',
    place: 'fragment'
};

/**
 * Billing connection
 * @see https://wiki.yandex-team.ru/Balance/Simple
 */
exports.billing = {
    url: 'http://balance-xmlrpc.yandex.net:8002/simpleapi/xmlrpc',
    token: 'mobile_yastore_22f7f32c7bd262ba38b31e755127399c'
};

/**
 * @see /routes/metrics.js
 */
exports.metrics = {
    '/registration': '784657',
    '/auth': '784657',
    '/registration/mail': '10053691'
};

exports.restore = {
    feedback: 'https://feedback2.yandex.ru/passport/spprstr/',
    blocked: 'https://feedback2.yandex.ru/passport/blocked/'
};

exports.audioCaptcha = {
    whitelist: ['KZ', 'UA', 'BY', 'RU', 'TR']
};

/**
 * Log level for the logs
 * @type {string}
 */
exports.loglevel = 'INFO';
exports.multiauth = true;
exports.multiauthPinning = true;
exports.intranet = true;

exports.appPasswordsClientIdMapping = {
    // Haha, no application passwords for ya-team
};

exports.corsAllowed = [
    'https://passport-test.yandex-team.ru',
    'https://oauth-test.yandex-team.ru',
    'https://tvm-test.yandex-team.ru'
];

exports.journalEventsLimits = {
    logLimit: 5,
    mapLimit: 999
};

exports.workspace = {
    zone: 'ws.yandex.%TLD%'
};

// Configs for security middlewares
exports.helmet = {
    csp: {
        directives: {
            defaultSrc: [CSP.NONE],
            styleSrc: [CSP.SELF, CSP.YASTATIC, CSP.UNSAFE_INLINE, CSP.UNSAFE_EVAL, CSP.S3_MDS, CSP.S3_MDST],
            scriptSrc: [
                CSP.SELF,
                CSP.YASTATIC,
                CSP.FINGERPRINT,
                CSP.METRIC,
                CSP.API_MAPS,
                CSP.SUGGEST_MAPS,
                function(req) {
                    const tld = CSP.TLD_REGEXP.exec(req.hostname);

                    if (!tld) {
                        return null;
                    }

                    return CSP.EXPORT_PREFIX + tld[1];
                },
                CSP.UNSAFE_EVAL,
                CSP.UNSAFE_INLINE,
                function(req, res) {
                    return `'nonce-${res.locals.nonce}'`; // CSPv2 nonce directive for inline scripts
                },
                CSP.BEATLE
            ],
            imgSrc: [
                CSP.SELF,
                CSP.YASTATIC,
                CSP.YSA_STATIC_TEST,
                CSP.YANDEX_ST,
                CSP.DATA,
                CSP.METRIC,
                CSP.API_MAPS,
                CSP.CAPTCHA,
                CSP.S3_MDS,
                CSP.S3_MDST,
                CSP.AVATARS_MDS,
                CSP.AVATARS_MDST,
                CSP.CLCK,
                CSP.MAPS,
                CSP.YAPIC,
                CSP.CENTER_YANDEX_TEAM,
                CSP.IMG_YANDEX_RU,
                CSP.STATIC_MAPS,
                CSP.BLOB,
                CSP.DOWNLOADER_YANDEX_TEST
            ],
            fontSrc: [CSP.SELF, CSP.YASTATIC],
            objectSrc: [CSP.YASTATIC],
            mediaSrc: [CSP.CAPTCHA, CSP.DATA],
            connectSrc: [
                function(req) {
                    const tld = CSP.TLD_REGEXP.exec(req.hostname);

                    if (!tld) {
                        return null;
                    }

                    return CSP.MAIL_PREFIX + tld[1];
                },
                CSP.SELF,
                CSP.TRUST_TEST,
                CSP.METRIC,
                CSP.SUGGEST_MAPS,
                CSP.YANDEX_RU,
                CSP.API_PASSPORT_TEST
            ],
            frameSrc: [
                CSP.SELF,
                CSP.BILLING_FRAME,
                CSP.MONEY_FRAME,
                function(req) {
                    const tld = CSP.TLD_REGEXP.exec(req.hostname);

                    if (!tld) {
                        return null;
                    }

                    return tld[1];
                },
                function(req) {
                    const tld = CSP.TLD_REGEXP.exec(req.hostname);

                    if (!tld) {
                        return null;
                    }

                    return CSP.PASS_PREFIX_PROD + tld[1];
                },
                CSP.FORM_YANDEX
            ],
            frameAncestors: [
                function(req) {
                    if (req.path !== '/auth/smarttv') {
                        return CSP.SELF;
                    }

                    return CSP.SELF;
                }
            ],
            childSrc: [
                CSP.SELF,
                function(req) {
                    const tld = CSP.TLD_REGEXP.exec(req.hostname);

                    if (!tld) {
                        return null;
                    }

                    return tld[1];
                },
                function(req) {
                    const tld = CSP.TLD_REGEXP.exec(req.hostname);

                    if (!tld) {
                        return null;
                    }

                    return CSP.PASS_PREFIX_PROD + tld[1];
                }
            ],
            reportUri: [
                (req) => {
                    return url.format({
                        protocol: 'https',
                        hostname: 'csp.yandex.net',
                        pathname: 'csp',
                        query: {
                            from: 'passport',
                            project: 'passport',
                            yandex_login: req.cookies.yandex_login,
                            yandexuid: req.cookies.yandexuid
                        }
                    });
                }
            ],
            manifestSrc: [CSP.SELF]
        },
        reportOnly: false
    },
    frameguard: 'DENY',
    noCache: {
        noEtag: true
    }
};

exports.experiments = common.experiments;

exports.links = common.links;

exports.secrets = {
    yamoney: common.yamoneySecret
};

exports.retries = common.retries;

exports.securityLevels = common.securityLevels;
exports.billingFrame = CSP.BILLING_FRAME;
exports.cspTldRegexp = CSP.TLD_REGEXP;
exports.geoCoderOrigin = common.geoCoderOrigin;
exports.cloudAPIToken = common.cloudAPIToken;
exports.connectAPIToken = common.connectAPIToken;
exports.ticketsFile = common.ticketsFile;
exports.neoPhonishPrefix = common.neoPhonishPrefix;
exports.ysaIdMap = common.ysaIdMap;
exports.signup = common.signup;
exports.sessguardDomains = common.sessguardDomains;
exports.otpSessionReissueInterval = common.otpSessionReissueInterval;
