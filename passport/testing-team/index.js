/*
    This is how you write the config:

    host: yandex.ru
    path: /whatso/ever
    url: https://yandex.ru/whatso/ever

    Items should be sorted alphabetically

 */
const url = require('url');
const loc = require('../_common/loc');
const documentationLinks = require('../_common/documentationLinks');
const CSP_NONE = "'none'";
const CSP_SELF = "'self'";
const CSP_UNSAFE_INLINE = "'unsafe-inline'";
const CSP_UNSAFE_EVAL = "'unsafe-eval'";
const CSP_DATA = 'data:';
const CSP_YASTATIC = 'yastatic.net';
const CSP_YANDEX_ST = 'yandex.st';
const CSP_FINGERPRINT = 'fingerprint-test.yandex-team.ru';
const CSP_PASSPORT = 'passport-test.yandex-team.ru';
const CSP_CAPTCHA = '*.captcha.yandex.net';
const CSP_AVATARS_MDS = 'avatars.mds.yandex.net';
const CSP_AVATARS_MDST = 'avatars.mdst.yandex.net';
const CSP_CLCK = 'clck.yandex.ru';
const CSP_YAPIC = 'yapic.yandex.ru';
const CSP_IMG_YANDEX_RU = 'img.yandex.ru';
const CSP_CENTER_YANDEX_TEAM = 'center.yandex-team.ru';
const CSP_METRIC = (function () {
    return ['ru', 'ua', 'by', 'kz', 'com', 'com.tr']
        .map(function (tld) {
            return 'mc.yandex.' + tld;
        })
        .join(' ');
})();
const CSP_AD_METRICA = 'mc.admetrica.ru';

module.exports = {
    env: 'testing-team',

    api: {
        oauth: {
            dao: {
                baseUrl: 'http://127.0.0.1:8302/iface_api',
                maxRetries: 3,
                maxConnections: 100,
                retryAfter: 500, // Milliseconds to wait before retrying
                retryCodes: ['backend.failed'],
                timeout: 8000
            }
        },
        passport: {
            dao: {
                baseUrl: 'http://passport-test-internal.yandex-team.ru',
                maxRetries: 5,
                maxConnections: 100,
                retryAfter: 100, // Milliseconds to wait before retrying
                retryCodes: ['blackboxfailed'],
                timeout: 8000
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
        }
    },

    avatar: {
        host: 'avatars.yandex.net',
        pathname: '/get-yapic/%uid%/islands-%size%'
    },

    mds: 'https://avatars.mdst.yandex.net/get-yapic/%avatarId%/islands-200',

    csrfSalt: 'ahpoohaijii5chee2jaeQuipheeGheixahfoolai5ahk2Ou1va2aiMohlae1rahv',

    hosts: {
        blackbox: 'blackbox-test.yandex-team.ru',
        mda: 'pass-test.yandex-team.ru'
    },

    loc,

    loglevel: 'verbose',

    paths: {
        static: 'https://yastatic.net/s3/passport-static/oauth/v{{VERSION}}',
        experiments: 'http://uaas.search.yandex.net/passport',
        passport: 'https://passport-test.yandex-team.%tld%/profile'
    },

    metricsID: '43642384',
    clientMetricsID: '50650357',

    appPasswordsClientIdMapping: {
        '4849d2dd746f45e5a51db43c6acb7c3d': 'calendar',
        '51d6ff8739bc4cab9a0f8d3ef4f4d620': 'disk',
        '0c276fa84a544fd19d404db94e16970d': 'mail',
        '00d8bc12be8544c788952624bc05c469': 'collector',
        '138b19038cd544ac8079e32a2590266c': 'chat'
    },

    documentationLinks
};

module.exports.helmet = {
    csp: {
        directives: {
            defaultSrc: [CSP_NONE],
            styleSrc: [CSP_YASTATIC, CSP_YANDEX_ST, CSP_UNSAFE_INLINE, CSP_UNSAFE_EVAL],
            scriptSrc: [
                CSP_YASTATIC,
                CSP_YANDEX_ST,
                CSP_METRIC,
                CSP_FINGERPRINT,
                CSP_UNSAFE_EVAL,
                (req, res) => `'nonce-${res.locals.nonce}'` // CSPv2 nonce directive for inline scripts
            ],
            imgSrc: [
                CSP_YASTATIC,
                CSP_YANDEX_ST,
                CSP_METRIC,
                CSP_DATA,
                CSP_CAPTCHA,
                CSP_AVATARS_MDS,
                CSP_AVATARS_MDST,
                CSP_CLCK,
                CSP_YAPIC,
                CSP_CENTER_YANDEX_TEAM,
                CSP_IMG_YANDEX_RU,
                CSP_AD_METRICA
            ],
            fontSrc: [CSP_DATA, CSP_YASTATIC],
            objectSrc: [CSP_YASTATIC],
            mediaSrc: [CSP_CAPTCHA, CSP_DATA],
            connectSrc: [CSP_SELF, CSP_PASSPORT, CSP_METRIC],
            frameSrc: [CSP_SELF, (_, res) => `yandex.${res.locals.selfTld}`],
            childSrc: [CSP_SELF],
            reportUri: function (req) {
                return url.format({
                    protocol: 'https',
                    hostname: 'csp.yandex.net',
                    pathname: 'csp',
                    query: {
                        from: 'oauth',
                        yandex_login: req.cookies.yandex_login,
                        yandexuid: req.cookies.yandexuid
                    }
                });
            }
        },
        reportOnly: false
    },
    frameguard: 'DENY',
    noCache: {
        noEtag: true
    }
};

module.exports.ticketsFile = '/var/cache/yandex/passport-tvm-keyring/oauth-frontend.tickets';
