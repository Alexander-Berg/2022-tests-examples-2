import {AppConfig} from 'yandex-cfg';

import testingCsp from './csp/testing';

const config: AppConfig = {
    csp: {
        presets: testingCsp,
    },
};

module.exports = config;
