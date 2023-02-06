import { AppConfig } from 'yandex-cfg';

import testingCsp from './csp/testing';

const config: AppConfig = {
    blackbox: {
        api: 'http://blackbox-mimino.yandex.net',
    },

    csp: {
        presets: testingCsp,
    },

    httpUatraits: {
        server: 'http://uatraits-test.qloud.yandex.ru',
    },

    secretkey: {
        salt: process.env.SECRET_KEY_SALT,
    },

    api: {
        serverUrl: 'https://demo-api.stands.ofd.yandex.net',
        timeout: 30 * 1000,
        retry: 2,
    },
};

module.exports = config;
