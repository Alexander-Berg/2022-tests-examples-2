const defaults = require('./default');

module.exports = {
    got: {
        rejectUnauthorized: false,
    },

    configs: {
        endpoint: 'http://configs.taxi.tst.yandex.net/configs/values',
        refreshInterval: 60 * 1000,
    },
    clientConfig: {
        oAuth: {},
    },

    csp: {
        ...defaults.csp,
        'img-src': defaults.csp['img-src'].concat(['avatars.mdst.yandex.net']),
    },
};
