import {AppConfig} from 'yandex-cfg';

import testingCsp from './csp/testing';

const config: AppConfig = {
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
};

module.exports = config;
