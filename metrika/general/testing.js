const csp = require('csp-presets-pack');

module.exports = {
    backend: {
        host: 'https://ofd.tst.yandex.ru'
    },

    blackbox: {
        api: 'blackbox-mimino.yandex.net'
    },

    bunker: {
        api: 'http://bunker-api-dot.yandex.net/v1',
        version: 'latest'
    },

    csp: {
        presets: {
            avatars: csp.avatars()
        }
    }
};
