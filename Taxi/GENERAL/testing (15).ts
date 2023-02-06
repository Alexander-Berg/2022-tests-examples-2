import {AppConfig} from 'yandex-cfg';

const config: AppConfig = {
    blackbox: {
        api: 'pass-test.yandex.ru',
    },

    tvm: {
        serverUrl: process.env.TVM_HOST,
        token: process.env.TVM_TOKEN,
    },

    environment: 'testing',
};

module.exports = config;
