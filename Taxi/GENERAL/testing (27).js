const defaults = require('./defaults');

module.exports = {
    clientConfig: {
        adminHost: 'https://ymsh-admin.tst.taxi.yandex-team.ru',
        stHost: 'https://st.test.yandex-team.ru',
        mapApi: '//api-maps.yandex.ru/2.1/?csp=true',
        taximeterHost: 'https://taximeter-admin.taxi.tst.yandex-team.ru',
        mdsHost: 'storage-int.mdst.yandex.net',
        kibanaHost: 'https://kibana.taxi.tst.yandex-team.ru',
        kibanaCronDashboard: 'http://kibana-logs.taxi.tst.yandex.net:5601/goto/1bb2823894b28c21a40b90cd6c41cf40',
        supchatHost: 'supchat.taxi.tst.yandex-team.ru',
        zendeskHost: 'yataxi1521460664.zendesk.com',
        zendeskHostYutaxi: 'yataxi1521460664.zendesk.com',
        fleetHost: 'https://fleet.tst.yandex-team.ru',
        groceryImagesHost: 'https://images.tst.grocery.yandex.net'
    },

    elastic: {
        servers: ['http://taxi-elastic-logs.taxi.tst.yandex.net:9200']
    },

    stClientOptions: {
        endpoint: 'https://st-api.test.yandex-team.ru/v2',
        clientOptions: {
            rejectUnauthorized: false
        }
    },

    csp: {
        ...defaults.csp,
        policies: {
            ...defaults.csp.policies,
            'script-src': [
                'tariff-editor.taxi.tst.yandex-team.ru/',
                ...defaults.csp.policies['script-src']
            ],
            'media-src': [
                ...defaults.csp.policies['media-src'],
                'promo-stories.s3.mdst.yandex.net',
                'promo-stories-testing.s3.mds.yandex.net'
            ],
            'img-src': [
                ...defaults.csp.policies['img-src'],
                'http://storage.mdst.yandex.net'
            ],
            'style-src': [
                ...defaults.csp.policies['style-src'],
                'https://supchat.taxi.dev.yandex-team.ru',
                'https://supchat.taxi.tst.yandex-team.ru',
                '*.front.taxi.dev.yandex-team.ru'
            ]
        }
    },

    api: {
        apiProxy: 'http://api-proxy.taxi.tst.yandex.net',
        adminPy2: 'https://ymsh-admin.tst.mobile.yandex-team.ru/api',
        adminPy3: 'http://taxi-api-admin.taxi.tst.yandex.net',
        backendConfigs: 'http://configs.taxi.tst.yandex.net',
        lenta: 'https://lenta.taxi.dev.yandex.net',
        infraEvents: 'http://infra-events.taxi.tst.yandex.net'
    },

    bunker: {
        api: 'http://bunker-api-dot.yandex.net/v1',
        version: 'latest',
        updateInterval: 5 * 60 * 1000
    }
};
