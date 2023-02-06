require('./addTypeScriptSupport');

const asyncConfig = JSON.parse(process.env.YA_SELENIUM_CONF);
const retries = Number.isNaN(+process.env.RETRIES)
    ? 4
    : parseInt(process.env.RETRIES, 10);
const baseUrl = `http://${asyncConfig.inHostname}:${asyncConfig.port}`;
const surfwaxHostname = 'sw.yandex-team.ru';
const gridUrl = `http://metrika@${surfwaxHostname}:80/v0`;

/*
    Нужно указать для локального запуска тестов пререндера.
    Если не указать, тесты в yabro будут пропущены.
    MacOs: /Applications/Yandex.app/Contents/MacOS/Yandex
 */
const yaBroBinary = process.env.YABRO_BINARY;
const DEBUG = !!process.env.E2E_DEBUG;
const SESSIONS_PER_BROWSER = Number(process.env.SESSIONS_PER_BROWSER) || 4;

module.exports = {
    system: {
        debug: DEBUG,
        ctx: {
            domains: asyncConfig.domains || [],
            domain: asyncConfig.inHostname,
            port: asyncConfig.port,
            schema: 'http',
        },
    },
    sessionRequestTimeout: 150000,
    baseUrl,
    prepareBrowser: (browser) => {
        browser.timeoutsAsyncScript(5000);
    },
    browsers: {
        chrome: {
            gridUrl: asyncConfig.useGrid ? gridUrl : undefined,
            desiredCapabilities: {
                timeouts: {
                    script: 5000,
                },
                browserName: 'chrome',
                version: '53.0',
            },
        },
        chromePerformance: {
            gridUrl: asyncConfig.useGrid ? gridUrl : undefined,
            desiredCapabilities: {
                timeouts: {
                    script: 1000,
                },
                sessionsPerBrowser: 10,
                browserName: 'chrome',
                version: '72.0',
            },
        },
        chromeIncognito: {
            gridUrl: asyncConfig.useGrid ? gridUrl : undefined,
            desiredCapabilities: {
                timeouts: {
                    script: 1000,
                },
                browserName: 'chrome',
                version: '53.0',
                chromeOptions: {
                    args: ['incognito'],
                },
            },
        },
        firefoxIncognito: {
            gridUrl: asyncConfig.useGrid ? gridUrl : undefined,
            // клиент и драйвер используют разные версии api
            // resetCursor: false позволяет в firefox не использовать moveTo (которого нет в новой версии драйвера)
            // в текущих тестах сброс курсора не влияет на поведение, поэтому он выключен
            // TODO: при необходимости использования методов - @yandex-int/wdio-polyfill
            resetCursor: false,
            desiredCapabilities: {
                timeouts: {
                    script: 1000,
                },
                browserName: 'firefox',
                version: '61.0',
                'moz:firefoxOptions': {
                    args: ['-private'],
                },
            },
        },
        chromeSuperApp: {
            gridUrl: asyncConfig.useGrid ? gridUrl : undefined,
            desiredCapabilities: {
                timeouts: {
                    script: 1000,
                },
                browserName: 'chrome',
                version: '53.0',
                chromeOptions: {
                    // Network emulation requires device mode, which is only enabled when mobile emulation is on
                    mobileEmulation: { deviceName: 'Laptop with touch' },
                },
                // Allow control over the state of network connectivity for testing
                networkConnectionEnabled: true,
            },
        },
        phone: {
            gridUrl: asyncConfig.useGrid ? gridUrl : undefined,
            desiredCapabilities: {
                timeouts: {
                    script: 1000,
                },
                browserName: 'chrome',
                version: '87.0',
                chromeOptions: {
                    mobileEmulation: {
                        deviceName: 'Pixel 2',
                    },
                },
            },
        },
        yandex: {
            gridUrl: asyncConfig.useGrid ? gridUrl : undefined,
            desiredCapabilities: {
                timeouts: {
                    script: 1000,
                },
                // Yandex browser
                browserName: 'chrome',
                version: '20.3.0.622',
                chromeOptions: {
                    binary: !asyncConfig.useGrid ? yaBroBinary : undefined,
                    args: [
                        'enable-features=NoStatePrefetch<ft',
                        'force-fieldtrials=ft/1',
                        'force-fieldtrial-params=ft.1:mode/prerender/link_mode/prerender',
                    ],
                },
            },
        },
    },
    retry: retries,
    sessionsPerBrowser: SESSIONS_PER_BROWSER,
    sets: {
        // run tests associated with this path in all browsers
        common: {
            // which are configured in the `browsers` option
            files: 'test/e2e/common',
            browsers: ['chrome'],
        },
        phone: {
            files: 'test/e2e/phone',
            browsers: ['phone'],
        },
        incognito: {
            files: 'test/e2e/incognito',
            browsers: ['chromeIncognito', 'firefoxIncognito'],
        },
        superapp: {
            files: 'test/e2e/superapp',
            browsers: ['chromeSuperApp'],
        },
        yandex: {
            files: 'test/e2e/yandex',
            browsers: [(yaBroBinary || asyncConfig.useGrid) && 'yandex'].filter(
                Boolean,
            ),
        },
        performance: {
            files: 'test/e2e/performance',
            browsers: ['chromePerformance'],
        },
    },
    plugins: {
        'html-reporter/hermione': {
            path: './test/e2e/report/common',
            saveErrorDetails: true,
        },
        '@yandex-int/hermione-surfwax-router': {
            enabled: Boolean(process.env.CI_SYSTEM),
            surfwaxHostname,
        },
    },
};
