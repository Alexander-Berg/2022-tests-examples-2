import { AppConfig } from 'yandex-cfg';

import { presets as cspPresets } from './csp/testing';

const config: AppConfig = {
    csp: {
        presets: cspPresets,
    },
};

module.exports = config;
