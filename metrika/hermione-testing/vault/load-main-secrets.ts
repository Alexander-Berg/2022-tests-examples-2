const { writeFileSync } = require('fs');

import cfg from 'yandex-cfg';

import {
    loadYamlConfig,
    loadYavSecrets,
} from '@metrika/server/load-configs';

(async function() {
    const yamlConfig = await loadYamlConfig(cfg.bishop);
    const secrets = yamlConfig.yav.secrets;
    await loadYavSecrets({ ...cfg.yav, secrets });

    const finalString = secrets.map(({to}: {to: string}) => {
        return `${to}=${process.env[to]}`;
    }).join('\n');

    writeFileSync(`${__dirname}/.env.main`, finalString);
})()
