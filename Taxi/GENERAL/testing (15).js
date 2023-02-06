const defaultConfig = require('./defaults');

module.exports = {
    csp: {
        policies: {
            ...defaultConfig.csp.policies,
            'img-src': [
                ...defaultConfig.csp.policies['img-src'],
                'avatars.mdst.yandex.net',
                'betastatic.yandex.net',
                'storage-int.mdst.yandex.net',
                'tc-tst.mobile.yandex.net',
                'tc.tst.mobile.yandex.net',
                'tc-unstable.tst.mobile.yandex.net',
                'ya-authproxy.taxi.tst.yandex.%tld%',
                'taxi-promotions-testing.s3.mdst.yandex.net'
            ],
            'connect-src': [
                ...defaultConfig.csp.policies['connect-src'],
                'passport-test.yandex.%tld%',
                'trust-test.yandex.%tld%',
                'ya-authproxy.taxi.tst.yandex.%tld%'
            ],
            'frame-src': [
                ...defaultConfig.csp.policies['frame-src'],
                '*.yandex.ru',
                '*.yandex.com',
                'trust-test.yandex.%tld%'
            ],
            'frame-ancestors': [...defaultConfig.csp.policies['frame-ancestors'], '*.yandex.com']
        }
    }
};
