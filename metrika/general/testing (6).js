'use strict';

const cspPresetTesting = require('./csp/presets/mds-testing');

module.exports = {
    bunker: {
        api: 'http://bunker-api-dot.yandex.net/v1',
        version: 'latest'
    },

    blackbox: {
        api: 'blackbox-mimino.yandex.net',
        avatarHost: 'https://avatars.mdst.yandex.net'
    },

    geobase: {
        server: 'http://geobase-test.qloud.yandex.ru'
    },

    langdetect: {
        server: 'http://langdetect-test.qloud.yandex.ru'
    },

    uatraits: {
        server: 'http://uatraits-test.qloud.yandex.ru'
    },

    csp: {
        extend: cspPresetTesting
    }
};
