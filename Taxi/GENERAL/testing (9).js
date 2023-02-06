const defaultConfig = require('./defaults');

const YANDEX_WHITE_LIST = ['*.yandex.ru', '*.yandex.com', '*.yandex.net', '*.yango.com'];

module.exports = {
    csp: {
        policies: {
            ...defaultConfig.csp.policies,
            'connect-src': [...defaultConfig.csp.policies['connect-src'], ...YANDEX_WHITE_LIST],
            'img-src': [
                ...defaultConfig.csp.policies['img-src'],
                'avatars.mdst.yandex.net',
                'betastatic.yandex.net',
                'https://storage-int.mdst.yandex.net',
                'https://tc-tst.mobile.yandex.net',
                'https://tc.tst.mobile.yandex.net',
                'https://tc-unstable.tst.mobile.yandex.net'
            ],
            'frame-src': [...defaultConfig.csp.policies['frame-src'], ...YANDEX_WHITE_LIST],
            'frame-ancestors': [
                ...defaultConfig.csp.policies['frame-ancestors'],
                ...YANDEX_WHITE_LIST,
                'http://localhost',
                'http://127.0.0.1',
                '*',
                'file://*'
            ]
        }
    }
};
