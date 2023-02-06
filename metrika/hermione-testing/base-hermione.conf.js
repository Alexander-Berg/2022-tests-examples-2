require('ts-node').register();
require('tsconfig-paths').register();

// загрузить в process.env данные для selenium grid и авторизации через паспорт
require('dotenv').config({ path: `${__dirname}/vault/.env.main` });

module.exports = {
    gridUrl: `http://${process.env.SELENIUM_USERNAME}:${process.env.SELENIUM_PASSWORD}@sg.yandex-team.ru:4444/wd/hub`,
    baseUrl: process.env.HERMIONE_HOST || 'https://test.metrika.yandex.ru',

    windowSize: {
        width: 1280,
        height: 1024,
    },

    waitTimeout: 10000,
    testsPerSession: 1,

    system: {
        ctx: {
            user: {
                username: process.env.HERMIONE_USERNAME,
                password: process.env.HERMIONE_PASSWORD,
            },
        },

        workers: 32,
    },

    browsers: {
        chrome: {
            desiredCapabilities: {
                browserName: 'chrome',
            },
        },
    },

    plugins: {
        'html-reporter/hermione': {
            path: 'html-report',
        },
    },
};
