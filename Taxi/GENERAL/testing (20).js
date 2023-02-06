const _ = require('lodash');
const baseConfig = require('_common/server/configs/testing');

module.exports = _.merge({}, baseConfig, {
    clientConfig: {
        newsAdminUrl: 'https://l7test.yandex.ru/blog/taxi'
    },

    models: {},

    csp: {
        policies: {
            ...baseConfig.csp.policies,
            'connect-src': [
                ...baseConfig.csp.policies['connect-src'],
                'taxi-frontend.taxi.dev.yandex.ru',
                'hiring-authproxy.taxi.tst.yandex.ru',
                '*.eda.tst.yandex.net',
                'trust-test.yandex.%tld%',
                'api.tap-tst.yandex.ru',
                'ya-authproxy.taxi.tst.yandex.%tld%',
                'api-maps.tst.c.maps.yandex.ru',
                'taxi.taxi.tst.yandex.ru',
                'maas.taxi.tst.yandex.net'
            ],
            'frame-ancestors': [...baseConfig.csp.policies['frame-ancestors'], '*.localhost.yandex.ru:4001'],
            'frame-src': [
                ...baseConfig.csp.policies['frame-src'],
                'taxi.yandex.%tld%',
                'trust-test.yandex.%tld%'
            ]
        }
    }
});
