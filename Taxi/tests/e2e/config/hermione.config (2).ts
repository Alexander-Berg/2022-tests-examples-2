import fs from 'fs';
import type Hermione from 'hermione';
import path from 'path';
import addUserRole from 'tests/e2e/config/commands/add-user-role';
import assertImage from 'tests/e2e/config/commands/assert-image';
import {deleteDownloadedFile, getDownloadedFile} from 'tests/e2e/config/commands/browser-file-action';
import clickInto from 'tests/e2e/config/commands/click-into';
import clipboardReadText from 'tests/e2e/config/commands/clipboard-read-text';
import dragAndDrop from 'tests/e2e/config/commands/drag-and-drop';
import {executeSql} from 'tests/e2e/config/commands/execute-sql';
import findByTestId from 'tests/e2e/config/commands/find-by-test-id';
import getPath from 'tests/e2e/config/commands/get-path';
import openPage from 'tests/e2e/config/commands/open-page';
import performScroll from 'tests/e2e/config/commands/perform-scroll';
import {processTaskQueue} from 'tests/e2e/config/commands/process-task-queue';
import typeInto from 'tests/e2e/config/commands/type-into';
import uploadFileInto from 'tests/e2e/config/commands/upload-file-into';
import {
    waitForTestIdSelectorInDom,
    waitForTestIdSelectorNotInDom,
    waitForTestIdSelectorNotVisible,
    waitForTestIdSelectorVisible
} from 'tests/e2e/config/commands/wait-for-test-id-selector-presence';
import {
    waitForTestIdSelectorAriaChecked,
    waitForTestIdSelectorAriaDisabled,
    waitForTestIdSelectorAriaEnabled,
    waitForTestIdSelectorAriaNotChecked,
    waitForTestIdSelectorClickable,
    waitForTestIdSelectorDisabled,
    waitForTestIdSelectorEnabled,
    waitForTestIdSelectorNotClickable,
    waitForTestIdSelectorReadyToPlayVideo
} from 'tests/e2e/config/commands/wait-for-test-id-selector-status';
import waitUntilRendered from 'tests/e2e/config/commands/wait-until-rendered';

import {PATH_TO_HERMIONE_HTML_REPORT} from '@/src/cli/test/constants';
import {serviceResolve} from '@/src/lib/resolve';

const pathToTests = serviceResolve('out/src/tests/e2e');
const transactionControlPlugin = path.resolve(pathToTests, 'hermione-transaction-control-plugin');
const htmlReporterPlugin = 'html-reporter/hermione';

const windowSize = {width: 1680, height: 1050};

const disableDownloadShelf = fs
    .readFileSync(path.resolve(__dirname, 'extensions', 'disable-download-shelf.crx').replace('/out', ''))
    .toString('base64');

const config: DeepPartial<Hermione.Config> = {
    sets: {e2e: {files: `${pathToTests}/**/*.hermione.js`}},
    browsers: {
        chromium: {
            desiredCapabilities: {
                browserName: 'chrome',
                browserVersion: '101.0',
                'selenoid:options': {
                    enableVNC: process.env.CI ? false : Boolean(process.env.VNC),
                    enableVideo: false,
                    enableLog: false,
                    // screenResolution: `${windowSize.width}x${windowSize.height}x24`,
                    hostsEntries: process.env.CI ? [] : ['host.docker.internal:host-gateway'],
                    name: 'pigeon-e2e'
                },
                'goog:chromeOptions': {
                    args: [
                        '--disable-setuid-sandbox',
                        '--disable-web-security',
                        '--accept-insecure-certificates',
                        '--disable-gpu',
                        `--window-size=${windowSize.width},${windowSize.height}`,
                        '--window-position=0,0',
                        '--no-sandbox'
                    ],
                    // Чтобы не прыгала высота в скриншотах:
                    //  * Скрывает системный диалог внизу окна браузера о том что был загружен файл
                    extensions: [disableDownloadShelf],
                    //  * Скрывает системный диалог вверху окна браузера о том что браузер управляется тестовым софтом
                    excludeSwitches: ['enable-automation']
                }
            }
        }
    },
    screenshotsDir: (test: Hermione.Test) =>
        path.join(path.dirname(test.file).replace('/out', ''), '__image_snapshots__'),
    gridUrl: `${process.env.SELENOID_DOMAIN}/wd/hub`,
    windowSize,
    screenshotDelay: 100,
    tolerance: 2.5,
    antialiasingTolerance: 8,
    screenshotMode: 'viewport',
    assertViewOpts: {allowViewportOverflow: true},
    sessionsPerBrowser: process.env.SESSIONS_PER_BROWSER ? Number(process.env.SESSIONS_PER_BROWSER) : undefined,
    retry: process.env.TEST_RETRY ? Number(process.env.TEST_RETRY) : 0,
    testTimeout: process.env.TEST_TIMEOUT ? Number(process.env.TEST_TIMEOUT) : null,
    waitTimeout: 5000,
    resetCursor: true,
    strictSSL: false,
    headless: true,
    plugins: {
        [transactionControlPlugin]: true,
        [htmlReporterPlugin]: {
            path: PATH_TO_HERMIONE_HTML_REPORT,
            saveErrorDetails: true,
            scaleImages: true
        }
    },
    system: {
        workers: process.env.SESSIONS_PER_BROWSER ? Number(process.env.SESSIONS_PER_BROWSER) : undefined
    },
    async prepareBrowser(browser: WebdriverIO.Browser) {
        browser.addCommand('clickInto', clickInto);
        browser.addCommand('processTaskQueue', processTaskQueue);
        browser.addCommand('typeInto', typeInto);
        browser.addCommand('findByTestId', findByTestId);
        browser.addCommand('waitForTestIdSelectorInDom', waitForTestIdSelectorInDom);
        browser.addCommand('waitForTestIdSelectorNotInDom', waitForTestIdSelectorNotInDom);
        browser.addCommand('waitForTestIdSelectorVisible', waitForTestIdSelectorVisible);
        browser.addCommand('waitForTestIdSelectorNotVisible', waitForTestIdSelectorNotVisible);
        browser.addCommand('waitForTestIdSelectorEnabled', waitForTestIdSelectorEnabled);
        browser.addCommand('waitForTestIdSelectorDisabled', waitForTestIdSelectorDisabled);
        browser.addCommand('waitForTestIdSelectorAriaDisabled', waitForTestIdSelectorAriaDisabled);
        browser.addCommand('waitForTestIdSelectorAriaEnabled', waitForTestIdSelectorAriaEnabled);
        browser.addCommand('waitForTestIdSelectorAriaChecked', waitForTestIdSelectorAriaChecked);
        browser.addCommand('waitForTestIdSelectorAriaNotChecked', waitForTestIdSelectorAriaNotChecked);
        browser.addCommand('waitForTestIdSelectorClickable', waitForTestIdSelectorClickable);
        browser.addCommand('waitForTestIdSelectorNotClickable', waitForTestIdSelectorNotClickable);
        browser.addCommand('waitForTestIdSelectorReadyToPlayVideo', waitForTestIdSelectorReadyToPlayVideo);
        browser.addCommand('waitUntilRendered', waitUntilRendered);
        browser.addCommand('uploadFileInto', uploadFileInto);
        browser.addCommand('assertImage', assertImage);
        browser.addCommand('openPage', openPage);
        browser.addCommand('getPath', getPath);
        browser.addCommand('getDownloadedFile', getDownloadedFile);
        browser.addCommand('deleteDownloadedFile', deleteDownloadedFile);
        browser.addCommand('dragAndDrop', dragAndDrop);
        browser.addCommand('performScroll', performScroll);
        browser.addCommand('executeSql', executeSql);
        browser.addCommand('clipboardReadText', clipboardReadText);
        browser.addCommand('addUserRole', addUserRole);
    }
};

module.exports = config;
