require('./addTypeScriptSupport');

const asyncConfig = JSON.parse(process.env.YA_SELENIUM_CONF);
const retries = Number.isNaN(+process.env.RETRIES)
    ? 5
    : parseInt(process.env.RETRIES, 10);
const baseUrl = `http://${asyncConfig.inHostname}:${asyncConfig.port}`;
const surfwaxHostname = 'sw.yandex-team.ru';
const gridUrl = `http://metrika@${surfwaxHostname}:80/v0`;
const DEBUG = !!process.env.E2E_DEBUG;
const SESSIONS_PER_BROWSER = Number(process.env.SESSIONS_PER_BROWSER) || 1;

/*
const testBrowsers = {
    chrome: {
        versions: [
            '87.0',
        ],
        capabilities: {
            browserName: 'chrome',
            chromeOptions: {
                args: ['ignore-certificate-errors'],
            },
        },
    }
};
*/
const BROWSERS = {
    chrome: {
        versions: [
            '50.0',
            '55.0',
            '60.0',
            '65.0',
            '75.0',
            '80.0',
            '84.0',
            '85.0',
            '86.0',
            '87.0',
        ],
        capabilities: {
            browserName: 'chrome',
            chromeOptions: {
                args: ['ignore-certificate-errors'],
            },
        },
    },
    firefox: {
        versions: ['60.0', '65.0', '66.0', '67.0', '68.0', '69.0'],
        capabilities: {
            browserName: 'firefox',
            acceptSslCerts: true,
            acceptInsecureCerts: true,
        },
    },
    yandex: {
        versions: ['19.9.3.358'],
        capabilities: {
            browserName: 'chrome',
            acceptSslCerts: true,
            acceptInsecureCerts: true,
        },
    },
    opera: {
        versions: ['49.0', '50.0', '55.0', '56.0', '57.0', '58.0'],
        capabilities: {
            browserName: 'opera',
            operaOptions: { binary: '/usr/bin/opera' },
        },
    },
};

const getBrowsersConfig = (browsers) => {
    return Object.keys(browsers).reduce((config, browserGroups) => {
        const { versions, options, capabilities } = browsers[browserGroups];

        versions.forEach((version) => {
            const fullName = `${browserGroups}-${version}`;

            // eslint-disable-next-line no-param-reassign
            config[fullName] = {
                gridUrl: asyncConfig.useGrid ? gridUrl : undefined,
                desiredCapabilities: {
                    proxy: asyncConfig.proxyPort
                        ? {
                              proxyType: 'manual',
                              httpProxy: `${asyncConfig.inHostname}:${asyncConfig.proxyPort}`,
                              sslProxy: `${asyncConfig.inHostname}:${asyncConfig.proxyPort}`,
                          }
                        : undefined,
                    timeouts: {
                        script: 3000,
                    },
                    version,
                    ...capabilities,
                },
                ...options,
            };
        });

        return config;
    }, {});
};

const BROWSERS_CONFIG = getBrowsersConfig(BROWSERS);

module.exports = {
    system: {
        parallelLimit: 5,
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
    browsers: BROWSERS_CONFIG,
    retry: retries,
    sessionsPerBrowser: SESSIONS_PER_BROWSER,
    sets: {
        smoke: {
            files: 'test/e2e/smoke',
            browsers: Object.keys(BROWSERS_CONFIG),
        },
    },
    plugins: {
        'html-reporter/hermione': {
            path: './test/e2e/report/smoke',
        },
        '@yandex-int/wdio-polyfill': {
            enabled: true,
            browsers: BROWSERS.firefox.versions.reduce((browsers, version) => {
                // eslint-disable-next-line no-param-reassign
                browsers[`firefox-${version}`] = ['moveTo'];

                return browsers;
            }, {}),
        },
        '@yandex-int/hermione-surfwax-router': {
            enabled: Boolean(process.env.CI_SYSTEM),
            surfwaxHostname,
        },
    },
};
