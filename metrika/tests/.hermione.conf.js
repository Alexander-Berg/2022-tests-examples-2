const RETRY = Number(process.env.RETRY) || 0;
const BETA_URL = process.env.BETA_URL || 'https://metrika-test.haze.yandex.ru';
const SESSIONS_PER_BROWSER = Number(process.env.SESSIONS_PER_BROWSER) || 1;
const HEADLESS = process.env.HEADLESS || false;
const GRID_URL = process.env.GRID_URL || 'http://localhost:4444/wd/hub';

const defaultTimeout = 90000;
const waitTimeout = 30000;

module.exports = {
    sets: {
        desktop: {
            files: [
                'tests/ft/e2e/*.js',
                'tests/ft/e2e/counters',
                'tests/ft/e2e/reports',
                'tests/ft/e2e/calls'
            ],
            browsers: ['chrome']
        }
    },
    baseUrl: BETA_URL,
    system: {
        ctx: {
            baseUrl: BETA_URL
        },
        workers: 30,
        testsPerWorker: 1
    },
    httpTimeout: defaultTimeout,
    sessionRequestTimeout: defaultTimeout,
    waitTimeout: waitTimeout,
    testsPerSession: 1,
    sessionsPerBrowser: SESSIONS_PER_BROWSER,
    browsers: {
        chrome: {
            desiredCapabilities: {
                browserName: 'chrome',
                acceptInsecureCerts: true,
                chromeOptions: HEADLESS
                    ? {
                        args: ['headless']
                    }
                    : undefined
            }
        }
    },
    retry: RETRY,
    gridUrl: GRID_URL,
    plugins: {
        'html-reporter/hermione': {
            enabled: true,
            path: './allure-results',
            defaultView: 'failed',
        }
    },
};
