import type {Options} from '@wdio/types';

export const specsConfig: Omit<Options.Testrunner, 'capabilities'> = {
    specs: ['./test/specs/**/*.ts'],
    exclude: [
        // 'path/to/excluded/files'
    ],

    // Define all options that are relevant for the WebdriverIO instance here
    logLevel: 'info',
    // Set specific log levels per logger
    // loggers:
    // - webdriver, webdriverio
    // - @wdio/browserstack-service, @wdio/devtools-service, @wdio/sauce-service
    // - @wdio/mocha-framework, @wdio/jasmine-framework
    // - @wdio/local-runner
    // - @wdio/sumologic-reporter
    // - @wdio/cli, @wdio/config, @wdio/utils
    // Level of logging verbosity: trace | debug | info | warn | error | silent
    // logLevels: {
    //     webdriver: 'info',
    //     '@wdio/appium-service': 'info'
    // },

    // If you only want to run your tests until a specific amount of tests have failed use
    // bail (default is 0 - don't bail, run all tests).
    bail: 0,

    // TODO: by env
    baseUrl: 'https://wfm.taxi.tst.yandex.ru',

    waitforTimeout: 10000,
    connectionRetryTimeout: 120000,
    connectionRetryCount: 3,
    services: ['chromedriver'],

    reporters: ['spec', ['allure', {outputDir: 'allure-results', tmsLinkTemplate: 'https://testpalm.yandex-team.ru/testcase/{}'}]],

    framework: 'mocha',
    mochaOpts: {
        ui: 'bdd',
        timeout: 60000,
    },
};
