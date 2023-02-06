import { Config } from 'hermione';
import { join } from 'path';
import { getSecretSync } from 'utils-configs/yav/index';
import { customWaitForRedirect } from './utils/waitFor/waitForRedirect';
import { customWaitForExist } from './utils/waitFor/waitForExist';
import { customWaitForEnabled } from './utils/waitFor/waitForEnabled';
import { customIsElementDisabled } from './utils/is/isElementDisabled';
import { customMoveTo } from './utils/move/moveTo';
import { customClearValue } from './utils/value/clearValue';
import { addCustomClick } from './utils/click/click';

const GRID_SECRET = 'sec-01dn2bxjwxxg3c1xsg2frd54ms';
const USER_SECRET = 'sec-01dnma2s9qh5b92tp7xy3xmbhh';

type Grid = {
    username: string;
    password: string;
};

type User = {
    username: string;
    password: string;
    oauth: string;
};

const grid: Grid = getSecretSync(GRID_SECRET);
const user: User = getSecretSync(USER_SECRET);

const RETRY = Number(process.env.RETRY) || 0;
const BETA_URL = process.env.BETA_URL ?? 'https://test.media.metrika.yandex.ru';
const SESSIONS_PER_BROWSER = Number(process.env.SESSIONS_PER_BROWSER) || 1;
const HEADLESS = process.env.HEADLESS ?? false;
const GRID_URL =
    process.env.GRID_URL ??
    `http://${grid.username}:${grid.password}@sg.yandex-team.ru:4444/wd/hub`;

const defaultTimeout = 90000;

const fullPathToPlugins = join(__dirname, 'plugins');
const configPluginPath = join(fullPathToPlugins, 'config');

const hermioneConfig: Config = {
    sets: {
        desktop: {
            files: ['tests/desktop'],
        },
    },
    baseUrl: BETA_URL,
    system: {
        ctx: {
            baseUrl: BETA_URL,
            user: {
                username: user.username,
                password: user.password,
                oauth: user.oauth,
            },
        },
        workers: 1,
        testsPerWorker: 1,
    },
    windowSize: {
        width: 1200,
        height: 1000,
    },
    httpTimeout: defaultTimeout,
    sessionRequestTimeout: defaultTimeout,
    waitTimeout: 30000,
    testsPerSession: 1,
    sessionsPerBrowser: SESSIONS_PER_BROWSER,
    screenshotsDir: 'tests/screens',
    browsers: {
        yabro: {
            desiredCapabilities: {
                browserName: 'chrome',
                acceptInsecureCerts: true,
                chromeOptions: {
                    binary: '/Applications/Yandex.app/Contents/MacOS/Yandex',
                },
            },
        },
        chrome: {
            desiredCapabilities: {
                browserName: 'chrome',
                acceptInsecureCerts: true,
                version: '68.0',
                chromeOptions: HEADLESS
                    ? {
                          args: ['headless'],
                      }
                    : undefined,
            },
        },
    },
    prepareBrowser(browser) {
        browser.addCommand('customWaitForRedirect', customWaitForRedirect);
        browser.addCommand('customWaitForExist', customWaitForExist);
        browser.addCommand('customWaitForEnabled', customWaitForEnabled);
        browser.addCommand('customIsElementDisabled', customIsElementDisabled);
        browser.addCommand('customMoveTo', customMoveTo);
        browser.addCommand('customClearValue', customClearValue);
        addCustomClick(browser);
    },
    retry: RETRY,
    gridUrl: GRID_URL,
    plugins: {
        'html-reporter/hermione': {
            enabled: true,
            path: './report-results',
            defaultView: 'failed',
        },
        [configPluginPath]: {},
    },
};

module.exports = hermioneConfig;
