const { writeFileSync } = require('fs');
const { execSyncJSON } = require('@metrika/utils-configs/cloud/exec');
import { getEnvSecrets } from './secrets';

const finalString = getEnvSecrets()
    .map(
        ({ name, version, key }) =>
            `${name}=${
                execSyncJSON(`ya vault get version ${version} -o ${key} -j`)[
                    key
                ]
            }`,
    )
    .join('\n');

writeFileSync(`${__dirname}/.env.initial`, finalString);
