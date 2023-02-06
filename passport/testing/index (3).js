const common = require('../common');
const url = require('url');
const _ = require('lodash');
const CSP = common.CSP;

exports.version = '{{VERSION}}';
exports.defaults = {
    url: {
        protocol: 'http',
        hostname: '127.0.0.1',
        port: '80',
        pathname: '/1/'
    },
    headers: {
        Host: 'passport-test-internal.yandex.ru',
        'User-Agent': 'got',
        'content-type': 'application/x-www-form-urlencoded'
    },
    qs: {
        consumer: 'passport'
    },
    method: 'POST',
    timeout: 10000
};

exports.dev = true;
exports.enablePlusDomain = true;

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
            baseUrl: 'http://oauth-test-internal.yandex.ru/iface_api',
            maxRetries: 3,
            maxConnections: 100,
            retryAfter: 500, // Milliseconds to wait before retrying
            retryCodes: ['backend.failed'],
            timeout: 8000
        }
    },
    passport: {
        dao: {
            baseUrl: url.format(_.assign({}, exports.defaults.url, {pathname: null})),
            maxRetries: 5,
            maxConnections: 100,
            retryAfter: 100, // Milliseconds to wait before retrying
            retryCodes: ['blackboxfailed'],
            timeout: exports.defaults.timeout
        }
    },
    disk: {
        dao: {
            baseUrl: 'http://sync01g.dst.yandex.net:8090',
            maxRetries: 5,
            maxConnections: 100,
            retryAfter: 100, // Milliseconds to wait before retrying
            timeout: 8000
        }
    },
    documents: {
        dao: {
            baseUrl: 'https://documents-test.pers.yandex.net',
            maxRetries: 5,
            maxConnections: 100,
            retryAfter: 100,
            timeout: 8000,
            agentOptions: {}
        }
    },
    cloud: {
        dao: {
            baseUrl: 'https://cloud-api.dst.yandex.net:8443',
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
            timeout: 8000,
            agentOptions: {
                rejectUnauthorized: false
            }
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
    billing: {
        dao: {
            baseUrl: 'http://music-web-ext.mt.yandex.net/internal-api',
            maxRetries: 5,
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
    avatars: {
        dao: {
            baseUrl: 'http://avatars-int.mdst.yandex.net:13000',
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
            maxRetries: 3,
            maxConnections: 100,
            retryAfter: 100, // Milliseconds to wait before retrying
            timeout: 1000
        }
    },
    familypay: {
        dao: {
            baseUrl: 'https://familypay-backend-test.so.yandex.net',
            maxRetries: 25,
            maxConnections: 100,
            retryAfter: 20, // Milliseconds to wait before retrying
            timeout: 1000
        }
    },
    antifraud: {
        dao: {
            baseUrl: 'https://fraud-test.so.yandex-team.ru',
            maxRetries: 5,
            maxConnections: 100,
            retryAfter: 100,
            timeout: 2000
        }
    },
    bnpl: {
        dao: {
            baseUrl: 'http://bnpl.fintech.tst.yandex.net',
            maxRetries: 2,
            maxConnections: 100,
            retryAfter: 100,
            timeout: 500
        }
    }
};

exports.fullname = {
    url: 'http://mail-extract-qa.cmail.yandex.net/?e=name',
    method: 'POST',
    jar: false,
    pool: {
        maxSockets: 100
    },
    timeout: 200
};

exports.langs = ['ru', 'uk', 'en', 'tr', 'id', 'fr', 'fi', 'kk', 'uz', 'az', 'he', 'ky', 'pt'];

exports.paths = {
    retpath: '/passport?mode=passport',
    basic: '/registration',
    static: '{{STATIC_PATH}}',
    blackbox: 'pass-test.yandex.ru',
    mda: 'sso.passport-test.yandex.ru',
    social_static: common.socialStatic,
    providers: 'http://social-test.yandex.ru/providers-domik.json',
    broker: 'https://social-test.yandex.%tld%/broker2/start',
    oauth: 'oauth-test.yandex.%tld%',
    plus: 'plus.tst.yandex.%tld%',
    passport: 'passport-test.yandex.%tld%',
    internal: 'passport-test-internal.yandex.ru',
    internalPort: '80',
    experiments: 'http://uaas.search.yandex.net/passport',
    mds: 'https://avatars.mdst.yandex.net',
    collectionsCard: 'https://yandex.ru/collections/card',
    collectionsUser: 'https://yandex.ru/collections/user',
    video: 'https://yandex.ru/video/favorites?filmId=%id%',
    avatar: {
        host: 'avatars.mdst.yandex.net',
        pathname: '/get-yapic/%uid%/islands-%size%',
        default_300: 'https://avatars.mdst.yandex.net/get-yapic/0/0-0/islands-300',
        avatar_300: 'https://avatars.mdst.yandex.net/get-yapic/%avatar_id%/islands-300'
    },
    ysa: {
        static: 'https://ysa-test-static.passport.yandex.ru',
        hostname: 'ysa-test.passport.yandex.net',
        port: '80'
    },
    yasms: 'http://phone-passport-test.yandex.ru',
    unread: {
        host: 'export.yandex.%tld%',
        pathname: '/for/unread.xml'
    },
    loginStatusPath: '/auth/login-status.html',
    bigbro: {
        hostname: 'bigbrother.yandex.net',
        port: '80'
    },
    help: {
        passport: 'https://yandex.%tld%/support/passport/',
        restore: 'https://yandex.%tld%/support/passport/',
        change_password: 'https://yandex.%tld%/support/passport/security/force-password-change.xml',
        change_password_form: 'https://yandex.%tld%/support/passport/security/force-password-change-form.xml',
        auth_challenges: 'https://yandex.%tld%/support/passport/security/login-challenge-form.xml',
        phones: 'https://www.yandex.%tld%/support/passport/authorization/phone.html',
        'restore-semiauto': 'https://yandex.%tld%/support/passport/support-restore.xml',
        kiddish: 'https://yandex.%tld%/support/kinopoisk/online/kids-mode.html'
    },
    logs: {
        graphite: '/var/log/yandex/passport-frontend/graphite.log',
        requests: '/var/log/yandex/passport-frontend/requests.log',
        accountVerification: '/var/log/yandex/passport-account-verification/data.log',
        accountVerificationPPL: '/var/log/yandex/passport-account-verification/data-ppl.log'
    },
    emailValidator: '//passport-test.yandex.%tld%/profile/emails/',
    embeddedauth: '//passport-test.yandex.%tld%/passport?mode=embeddedauth',
    yamoney: {
        hostname: 'shiro.yandex1.ymdev.yandex.ru',
        port: 8081
    },
    amExperiments: {
        hostname: 'uaas-test.passport.yandex.net',
        port: 80,
        pathname: '/1/bundle/experiments/by_device_id/'
    },
    mapsAPI: 'https://api-maps.yandex.ru/2.1/?lang=%lang%&mode=debug',
    yamoneyCards: 'https://money.yandex.%tld%/cards',
    tunePlaces: common.tunePlaces,
    marketAddresses: common.marketAddresses,
    staticMaps: common.staticMaps,
    authCustomsStatic: 'https://yastatic.net/s3/passport-auth-customs/',
    magicQrUrl: 'https://magic.passport-test.yandex.ru',
    accountsUrl: '//api.passport-test.yandex.%tld%/all_accounts',
    yaPayLanding: common.yaPayLanding
};

exports.intranetPaths = {
    retpath: '/passport?mode=passport',
    blackbox: 'pass-test.yandex.ru',
    mda: 'pass-test.yandex.ru'
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
    url: 'http://greed-tm1f.yandex.ru:8002/simpleapi/xmlrpc',
    token: 'mobile_yastore_22f7f32c7bd262ba38b31e755127399c'
};

/**
 * @see /routes/metrics.js
 */
exports.metrics = {
    '/': '30479502'
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

exports.appPasswordsClientIdMapping = {
    '0c276fa84a544fd19d404db94e16970d': 'mail',
    '51d6ff8739bc4cab9a0f8d3ef4f4d620': 'disk',
    '0d0b33f918244b6394da3224334e4671': 'addrbook',
    '4849d2dd746f45e5a51db43c6acb7c3d': 'calendar',
    '138b19038cd544ac8079e32a2590266c': 'chat',
    bb1c044ac84d4e4f9f1c2de36d2b003b: 'magnitola',
    '00d8bc12be8544c788952624bc05c469': 'collector'
};

exports.corsAllowed = [
    'https://passport-test.yandex',
    'https://oauth-test.yandex',
    'https://tvm-test.yandex',
    'https://xtave.oauth-dev-bionic.yandex',
    'https://oauth-dev-bionic.yandex'
].reduce((acc, service) => {
    [
        'az',
        'com.am',
        'com.ge',
        'co.il',
        'kg',
        'lv',
        'lt',
        'md',
        'tj',
        'tm',
        'uz',
        'fr',
        'ee',
        'eu',
        'ru',
        'ua',
        'by',
        'kz',
        'com',
        'com.tr'
    ].forEach((tld) => {
        acc.push(`${service}.${tld}`);
    });
    return acc;
}, []);

exports.journalEventsLimits = {
    logLimit: 5,
    mapLimit: 999
};

exports.workspace = {
    zone: 'yaconnect.com'
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
                CSP.METRIC,
                CSP.CHAT,
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
                CSP.YANDEX_ST,
                CSP.YSA_STATIC_TEST,
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
                CSP.IMG_YANDEX_RU,
                CSP.STATIC_MAPS,
                CSP.VIDEO_TUB,
                CSP.BLOB,
                CSP.DOWNLOADER_YANDEX_TEST
            ],
            fontSrc: [CSP.SELF, CSP.YASTATIC, CSP.DATA],
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
                CSP.API_PASSPORT_TEST,
                CSP.UPLOAD_DISK_YANDEX_TEST
            ],
            frameAncestors: [CSP.FRAME_ANCESTORS],
            frameSrc: [
                CSP.SELF,
                CSP.MONEY_FRAME,
                CSP.MESSENGER_FRAME_DEV,
                CSP.BNPL_FRAME_TEST,
                function(req) {
                    const tld = CSP.TLD_REGEXP.exec(req.hostname);

                    if (!tld) {
                        return null;
                    }

                    return tld[1];
                },
                function(req) {
                    const tld = CSP.TLD_REGEXP.exec(req.hostname);

                    if (
                        tld &&
                        ['yandex.ua', 'yandex.by', 'yandex.kz'].indexOf(tld[1]) > -1 &&
                        req.cookies.mda !== '0'
                    ) {
                        return [
                            `${req.hostname.replace(tld[1], 'yandex.ru')}`,
                            `${CSP.PASS_PREFIX_TEST}${tld[1]}`,
                            `${CSP.PASS_PREFIX_TEST}yandex.ru`,
                            'passport-test.yandex.ru'
                        ].join(' ');
                    }

                    return null;
                },
                function(req) {
                    const tld = CSP.TLD_REGEXP.exec(req.hostname);

                    if (!tld) {
                        return null;
                    }

                    return CSP.PASS_PREFIX_TEST + tld[1];
                },
                function(req) {
                    const tld = CSP.TLD_REGEXP.exec(req.hostname);

                    if (!tld) {
                        return null;
                    }

                    return `passport-test.${tld[1]}`;
                },
                function(req) {
                    const tld = CSP.TLD_REGEXP.exec(req.hostname);

                    if (!tld) {
                        return null;
                    }

                    return CSP.BILLING_PREFIX_TEST + tld[1];
                },
                'blob:',
                'mc.yandex.ru',
                function(req) {
                    const tld = CSP.TLD_REGEXP.exec(req.hostname);

                    if (!tld) {
                        return null;
                    }

                    return `${CSP.MAGIC_PREFIX}-test.${tld[1]}`;
                },
                CSP.FORM_YANDEX
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

                    if (
                        tld &&
                        ['yandex.ua', 'yandex.by', 'yandex.kz'].indexOf(tld[1]) > -1 &&
                        req.cookies.mda !== '0'
                    ) {
                        return [
                            `${req.hostname.replace(tld[1], 'yandex.ru')}`,
                            `${CSP.PASS_PREFIX_TEST}${tld[1]}`,
                            `${CSP.PASS_PREFIX_TEST}yandex.ru`,
                            'passport-test.yandex.ru'
                        ].join(' ');
                    }

                    return null;
                },
                function(req) {
                    const tld = CSP.TLD_REGEXP.exec(req.hostname);

                    if (!tld) {
                        return null;
                    }

                    return CSP.PASS_PREFIX_TEST + tld[1];
                },
                function(req) {
                    const tld = CSP.TLD_REGEXP.exec(req.hostname);

                    if (!tld) {
                        return null;
                    }

                    return `passport-test.${tld[1]}`;
                },
                function(req) {
                    const tld = CSP.TLD_REGEXP.exec(req.hostname);

                    if (!tld) {
                        return null;
                    }

                    return CSP.BILLING_PREFIX_TEST + tld[1];
                },
                'blob:',
                'mc.yandex.ru'
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

exports.plusAvailableTld = ['ru', 'kz', 'by'];

exports.plusAvailableCountries = {
    225: 'ru',
    159: 'kz',
    149: 'by'
};

exports.experiments = common.experiments;

exports.links = common.links;

exports.secrets = {
    yamoney: 'yandex12345'
};

exports.retries = common.retries;

exports.securityLevels = common.securityLevels;
exports.cloudAPIToken = common.cloudAPIToken;
exports.connectAPIToken = common.connectAPIToken;
exports.billingFrame = CSP.BILLING_PREFIX;
exports.cspTldRegexp = CSP.TLD_REGEXP;
exports.geoCoderOrigin = common.geoCoderOrigin;
exports.ticketsFile = common.ticketsFile;
exports.neoPhonishPrefix = common.neoPhonishPrefix;
exports.subscriptions = common.subscriptions;
exports.ysaIdMap = common.ysaIdMap;
exports.signup = common.signup;
exports.otpSessionReissueInterval = common.otpSessionReissueInterval;
