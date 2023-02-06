const defaultConfig = require('./defaults.common');

module.exports = {
    csp: {
        policies: {
            ...defaultConfig.csp.policies,
            'img-src': [
                ...defaultConfig.csp.policies['img-src'],
                'https://tc-tst.mobile.yandex.net',
                'https://tc.tst.mobile.yandex.net',
                'https://tc-unstable.tst.mobile.yandex.net',
                'avatars.mdst.yandex.net'
            ],
            'connect-src': [
                ...defaultConfig.csp.policies['connect-src'],
                'ya-authproxy.taxi.tst.yandex.%tld%'
            ]
        }
    }
};
