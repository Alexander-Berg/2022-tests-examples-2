import {AppConfig} from 'yandex-cfg';

import testingCsp from './csp/testing';

const config: AppConfig = {
    api: {
        timeout: 10000,
    },

    blackbox: {
        api: 'pass-test.yandex.ru',
    },

    bunker: {
        api: 'http://bunker-api-dot.yandex.net/v1',
        version: 'latest',
    },

    csp: {
        presets: testingCsp,
    },

    httpGeobase: {
        server: 'http://geobase-test.qloud.yandex.ru',
    },

    httpLangdetect: {
        server: 'http://langdetect-test.qloud.yandex.ru',
    },

    httpUatraits: {
        server: 'http://uatraits-test.qloud.yandex.ru',
    },

    static: {
        baseUrl: `/s3-api/${process.env.APP_VERSION}/client/`,
        frozenPath: '/_',
        version: '',
    },

    tvm: {
        serverUrl: process.env.TVM_HOST,
        token: process.env.TVM_TOKEN,
    },
};

module.exports = config;
