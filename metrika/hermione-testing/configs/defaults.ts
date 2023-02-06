import { AppConfig } from 'yandex-cfg';

// загрузить в process.env токены: YAV_OAUTH_TOKEN BISHOP_OAUTH_TOKEN
require('dotenv').config({ path: `${__dirname}/../vault/.env.initial` });

const config: AppConfig = {
    version: process.env.APP_VERSION,

    bishop: {
        server: 'https://bishop.mtrs.yandex-team.ru/api/v2/config',
        program: process.env.BISHOP_PROGRAM_NAME ?? 'hermione-frontend',
        environment:
            process.env.BISHOP_ENVIRONMENT_NAME ??
            'metrika.deploy.frontend.hermione-testing',
        mergePriority: 'remote',
        clientOptions: {
            headers: {
                Authorization: `OAuth ${process.env.BISHOP_OAUTH_TOKEN}`,
            },
            retry: 5,
            timeout: 10000,
            throwHttpErrors: true,
        },
    },

    yav: {
        server: 'https://vault-api.passport.yandex.net/1',
        clientOptions: {
            headers: {
                Authorization: `OAuth ${process.env.YAV_OAUTH_TOKEN}`,
            },
            throwHttpErrors: true,
        },
    },
};

module.exports = config;
