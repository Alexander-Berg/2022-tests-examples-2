const merge = require('deepmerge');
const allureReporter = require('@wdio/allure-reporter').default;

const baseUrl = process.env.LOGISTIC_HOSTNAME
    ? process.env.LOGISTIC_HOSTNAME
    : 'https://logistics-frontend.taxi.tst.yandex.ru';

const browsers = {
    grid: {
        logLevel: 'error',
        hostname: 'qa-taxi-frontend@sw.yandex-team.ru',
        path: '/wd/v1/quotas/qa-taxi-frontend',
        port: 80,
        headers: {Authorization: `OAuth ${process.env.SURFWAX_TOKEN}`},
        capabilities: [
            {
                maxInstances: 15,
                browserName: 'chrome',
                browserVersion: '96.0',
                'goog:chromeOptions': {
                    args: [
                        '--disable-gpu',
                        '--lang=ru',
                        '--window-size=1920,1080',
                        '--disable-infobars',
                        '--disable-web-security',
                        '--disable-popup-blocking'
                    ],
                    prefs: {
                        'profile.default_content_setting_values.geolocation': 2
                    }
                },
                'selenoid:options': {
                    env: ['LANG=ru_RU.UTF-8', 'LANGUAGE=ru:en', 'LC_ALL=ru_RU.UTF-8'],
                    enableVNC: true,
                    enableVideo: true
                },
                acceptInsecureCerts: true,
                specs: [
                    './tests/order/desktop/*.js',
                    './tests/order/all-resolutions/*.js',
                    './tests/account/*.js',
                    './tests/phoenix/*.js',
                    './tests/shared-route/*.js'
                ]
            },
            {
                maxInstances: 5,
                browserName: 'chrome',
                browserVersion: '96.0',
                'goog:chromeOptions': {
                    mobileEmulation: {deviceName: 'iPhone X'},
                    args: [
                        '--disable-gpu',
                        '--lang=ru',
                        '--disable-infobars',
                        '--disable-web-security',
                        '--disable-popup-blocking'
                    ],
                    prefs: {
                        'profile.default_content_setting_values.geolocation': 2
                    }
                },
                'selenoid:options': {
                    env: ['LANG=ru_RU.UTF-8', 'LANGUAGE=ru:en', 'LC_ALL=ru_RU.UTF-8'],
                    enableVNC: true,
                    enableVideo: true,
                    screenResolution: '800x800x24'
                },
                acceptInsecureCerts: true,
                specs: [
                    './tests/order/mobile/*.js',
                    './tests/order/all-resolutions/*.js',
                    './tests/shared-route/*.js'
                ]
            }
        ],
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
        runner: 'local',
        reporters: ['spec'],
        logLevel: 'error',
        capabilities: [
            {
                maxInstances: 5,
                browserName: 'chromium',
                'goog:chromeOptions': {
                    args: [
                        '--disable-gpu',
                        '--disable-infobars',
                        '--lang=ru',
                        '--auto-open-devtools-for-tabs',
                        '--window-size=1920,1080',
                        '--headless'
                    ],
                    prefs: {
                        'profile.default_content_setting_values.geolocation': 2
                    }
                },
                acceptInsecureCerts: true,
                specs: [
                    './tests/order/desktop/*.js',
                    './tests/order/all-resolutions/*.js',
                    './tests/account/*.js',
                    './tests/phoenix/*.js'
                ]
            },
            {
                maxInstances: 5,
                browserName: 'chromium',
                'goog:chromeOptions': {
                    mobileEmulation: {deviceName: 'iPhone X'},
                    args: ['--headless'],
                    prefs: {
                        'profile.default_content_setting_values.geolocation': 2
                    }
                },
                acceptInsecureCerts: true,
                specs: ['./tests/order/mobile/*.js', './tests/order/all-resolutions/*.js']
            }
        ]
    },
    debug: {
        reporters: ['spec'],
        logLevel: 'info',
        capabilities: [
            {
                maxInstances: 1,
                browserName: 'chrome',
                browserVersion: '96.0',
                'goog:chromeOptions': {
                    // mobileEmulation: {deviceName: 'iPhone X'},
                    args: [
                        '--disable-gpu',
                        '--disable-infobars',
                        '--lang=ru',
                        '--auto-open-devtools-for-tabs',
                        '--window-size=1920,1080'
                    ],
                    prefs: {
                        'profile.default_content_setting_values.geolocation': 2
                    }
                },
                acceptInsecureCerts: true
            }
        ]
    }
};

const config = {
    exclude: [],
    maxInstances: 20,
    bail: 0,
    baseUrl: baseUrl,
    waitforTimeout: 10000,
    connectionRetryTimeout: 150000,
    connectionRetryCount: 3,
    services: [],
    framework: 'mocha',
    mochaOpts: {
        ui: 'bdd',
        timeout: 60000
    },
    afterTest: async function (test, context, {error, result, duration, passed, retries}) {
        await browser.takeScreenshot();

        // из грида всегда возвращается одна версия браузера, поэтому аллюр не разбивает тесты на мобильные и десктоп
        // для мобилки задается screenResolution при запуске, а тут его сравниваем и тегаем
        let windowSize = await browser.getWindowSize();
        if (windowSize.height < 801) {
            await allureReporter.addArgument('chrome', 'mobile');
        }

        allureReporter.addStep('Grid video: https://sw.yandex-team.ru/video/' + browser.sessionId);

        await browser.mockRestoreAll();
    }
};

exports.config = merge.all([config, browsers[process.env.RUNNER || 'local']]);
