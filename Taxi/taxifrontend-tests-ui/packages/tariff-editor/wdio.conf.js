const merge = require('deepmerge');
const getUsersFile = require('./support/getUsersFile');
const allureReporter = require('@wdio/allure-reporter').default;

const runner = {
    local: {
        runner: 'local'
    },
    grid: {
        hostname: 'qa-taxi-frontend@sw.yandex-team.ru',
        path: '/wd/v1/quotas/qa-taxi-frontend',
        port: 80,
        headers: {Authorization: `OAuth ${process.env.SURFWAX_TOKEN}`}
    }
};

const browsers = {
    grid: {
        capabilities: [
            {
                maxInstances: 10,
                browserName: 'chrome',
                browserVersion: '96.0',
                'goog:chromeOptions': {
                    args: ['--lang=ru', '--window-size=1920,1080', '--disable-infobars']
                },
                'selenoid:options': {
                    env: ['LANG=ru_RU.UTF-8', 'LANGUAGE=ru:en', 'LC_ALL=ru_RU.UTF-8'],
                    enableVNC: process.env.TEST_SPECS !== 'screen',
                    enableVideo: process.env.TEST_SPECS !== 'screen'
                },
                acceptInsecureCerts: true
            }
        ],
        mochaOpts: {
            ui: 'bdd',
            timeout: 60000,
            retries: 1
        },
        reporters: [
            [
                'allure',
                {
                    outputDir: 'allure-results',
                    disableWebdriverStepsReporting: true,
                    tmsLinkTemplate: 'https://testpalm.yandex-team.ru/testcase/{}'
                }
            ]
        ],
        specFileRetries: 1,
        specFileRetriesDelay: 0,
        specFileRetriesDeferred: true
    },
    local: {
        capabilities: [
            {
                maxInstances: 1,
                browserName: 'chrome',
                browserVersion: '96.0',
                'goog:chromeOptions': {
                    args: ['--lang=ru', '--window-size=1920,1080', '--disable-infobars']
                },
                'selenoid:options': {
                    env: ['LANG=ru_RU.UTF-8', 'LANGUAGE=ru:en', 'LC_ALL=ru_RU.UTF-8'],
                    enableVNC: false,
                    enableVideo: false
                },
                acceptInsecureCerts: true
            }
        ],
        mochaOpts: {
            ui: 'bdd',
            timeout: 60000,
            retries: 0
        },
        reporters: ['spec']
    }
};

const specs = {screen: ['./screen-tests/*.js'], e2e: ['./test/*/*.js']};

const config = {
    async onPrepare() {
        await getUsersFile('./users.json');
    },
    specs: specs[process.env.TEST_SPECS || 'e2e'],
    exclude: [],
    baseUrl: 'https://tariff-editor.taxi.tst.yandex-team.ru',
    maxInstances: 10,
    logLevel: 'error',
    bail: 0,
    waitforTimeout: 10000,
    connectionRetryTimeout: 120000,
    connectionRetryCount: 3,
    services: [
        [
            'image-comparison',
            {
                baselineFolder: './screenshots/baseline',
                formatImageName: '{tag}',
                screenshotPath: './screenshots/',
                autoSaveBaseline: true,
                returnAllCompareData: true,
                logLevel: 'silent'
            }
        ]
    ],
    framework: 'mocha',
    afterTest: async function (test, context, {error, result, duration, passed, retries}) {
        await browser.takeScreenshot();
        if (process.env.TEST_SPECS !== 'screen') {
            allureReporter.addStep(
                'Grid video: https://sw.yandex-team.ru/video/' + browser.sessionId
            );
        }
    }
};

exports.config = merge.all([
    config,
    runner[process.env.RUNNER || 'local'],
    browsers[process.env.RUNNER || 'local']
]);
