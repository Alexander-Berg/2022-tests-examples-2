var defaultConfig = require('./default');

module.exports = {
    bunker: {
        version: 'latest',
        updateInterval: 30000
    },

    blackbox: {
        api: 'blackbox-mimino.yandex.net',
        tvmID:  239
    },

    mail: {
        smtp: 'outbound-relay.yandex.net'
    },
    blogs: {
        host: 'https://yablogs-api-test.common.yandex.ru/v1',
        site: 'https://l7test.yandex.com/blog/metrica/',
        tvmID: 2000081
    },
    tvm: {
        clientId: 2015373,
        host: 'https://tvm-api.yandex.net/2',
    },
    metrikaCounters: defaultConfig.metrikaCounters.map(function (counter) {
        if (counter.id === defaultConfig.demoCounter) {
            counter.id = '43965669';
        }
        return counter;
    })
};
