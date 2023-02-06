require('./addTypeScriptSupport');

const asyncConfig = JSON.parse(process.env.YA_SELENIUM_CONF);
const retries = Number.isNaN(+process.env.RETRIES)
    ? 4
    : parseInt(process.env.RETRIES, 10);
const baseUrl = `http://${asyncConfig.inHostname}:${asyncConfig.port}`;
const surfwaxHostname = 'sw.yandex-team.ru';
const gridUrl = `http://metrika@${surfwaxHostname}:80/v0`;
const DEBUG = !!process.env.E2E_DEBUG;
const SESSIONS_PER_BROWSER = Number(process.env.SESSIONS_PER_BROWSER) || 1;

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
    browsers: {
        chrome: {
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
                    script: 1000,
                },
                browserName: 'chrome',
                version: '53.0',
            },
        },
        securitypolicy: {
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
                    script: 10000,
                },
                browserName: 'chrome',
                version: '72.0',
            },
        },
        chromeHeadlessFakeAndroid: {
            gridUrl: asyncConfig.useGrid ? gridUrl : undefined,
            desiredCapabilities: {
                proxy: asyncConfig.proxyPort
                    ? {
                          proxyType: 'manual',
                          httpProxy: `${asyncConfig.inHostname}:${asyncConfig.proxyPort}`,
                          sslProxy: `${asyncConfig.inHostname}:${asyncConfig.proxyPort}`,
                      }
                    : undefined,
                chromeOptions: {
                    args: [
                        'headless',
                        'user-agent="Android Version/0.0 Chrome/0.0"',
                    ],
                },
                timeouts: {
                    script: 1000,
                },
                browserName: 'chrome',
                version: '53.0',
            },
        },
        validForCrossDomains: {
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
                    script: 1000,
                },
                browserName: 'chrome',
                version: '53.0',
                chromeOptions: {
                    args: ['headless', 'user-agent="It is Yptp/1.52 "'],
                },
            },
        },
        bot: {
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
                    script: 1000,
                },
                browserName: 'chrome',
                version: '53.0',
                chromeOptions: {
                    args: [
                        'user-agent="Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)"',
                    ],
                },
            },
        },
        itp: {
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
                    script: 1000,
                },
                browserName: 'chrome',
                version: '53.0',
                chromeOptions: {
                    args: ['user-agent="iPhone OS 15_15"'],
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
            files: 'test/e2e/proxy',
            browsers: ['chrome'],
        },
        deviceSync: {
            files: 'test/e2e/deviceSync',
            browsers: ['chromeHeadlessFakeAndroid'],
        },
        crossdomain: {
            files: 'test/e2e/crossDomain',
            browsers: ['validForCrossDomains'],
        },
        bot: {
            files: 'test/e2e/bot',
            browsers: ['bot'],
        },
        itp: {
            files: 'test/e2e/itp',
            browsers: ['itp'],
        },
        securitypolicy: {
            files: 'test/e2e/securitypolicy',
            browsers: ['securitypolicy'],
        },
    },
    plugins: {
        'html-reporter/hermione': {
            path: './test/e2e/report/proxy',
        },
        '@yandex-int/hermione-surfwax-router': {
            enabled: Boolean(process.env.CI_SYSTEM),
            surfwaxHostname,
        },
    },
};
