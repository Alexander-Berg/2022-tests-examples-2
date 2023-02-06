import {EventEmitter} from 'events';
import fs from 'fs';
import type Hermione from 'hermione';
import path from 'path';
import {assertBySelector} from 'tests/e2e/config/commands/assert-by-selector';
import {assertImage} from 'tests/e2e/config/commands/assert-image';
import {deleteDownloadedFile, getDownloadedFile} from 'tests/e2e/config/commands/browser-file-action';
import {clickInto, clickIntoEnsured} from 'tests/e2e/config/commands/click-into';
import {dragAndDrop} from 'tests/e2e/config/commands/drag-and-drop';
import {executeSql} from 'tests/e2e/config/commands/execute-sql';
import {getPath} from 'tests/e2e/config/commands/get-path';
import {hideBySelector} from 'tests/e2e/config/commands/hide-by-selector';
import {moveMouseTo} from 'tests/e2e/config/commands/move-mouse-to';
import {openPage} from 'tests/e2e/config/commands/open-page';
import {performScroll} from 'tests/e2e/config/commands/perform-scroll';
import {processTaskQueue} from 'tests/e2e/config/commands/process-task-queue';
import {removeByTestId} from 'tests/e2e/config/commands/remove-by-test-id';
import {showBySelector} from 'tests/e2e/config/commands/show-by-selector';
import {typeInto} from 'tests/e2e/config/commands/type-into';
import {uploadFileInto} from 'tests/e2e/config/commands/upload-file-into';
import {
    waitForTestIdSelectorInDom,
    waitForTestIdSelectorNotInDom
} from 'tests/e2e/config/commands/wait-for-test-id-selector-presence';
import {
    waitForTestIdSelectorAriaChecked,
    waitForTestIdSelectorAriaDisabled,
    waitForTestIdSelectorClickable,
    waitForTestIdSelectorDisabled,
    waitForTestIdSelectorEnabled,
    waitForTestIdSelectorNotClickable
} from 'tests/e2e/config/commands/wait-for-test-id-selector-status';
import {waitUntilRendered} from 'tests/e2e/config/commands/wait-until-rendered';
import {enableDevtoolsNetworkPlainWS} from 'tests/e2e/utils/devtools/devtools-plain-ws';

import {PATH_TO_HERMIONE_HTML_REPORT} from '@/src/cli/test/constants';
import {resolve} from '@/src/lib/resolve';

import {checkForExistenceByTestId} from './commands/check-for-existence-by-test-id';
import {waitForTestIdSelectorDisplayed} from './commands/wait-for-test-id-selector-displayed';

const {
    CI,
    SELENOID_HOST,
    TEST_RETRY,
    TEST_TIMEOUT,
    E2E_LOG_NETWORK_EVENTS,
    E2E_LOG_RESPONSE_BODY,
    E2E_ENABLE_SELENOID_LOG
} = process.env;

const testsPerWorker = 15;
EventEmitter.defaultMaxListeners = testsPerWorker;

const pathToTests = resolve('out/src/tests/e2e');
const transactionControlPlugin = path.resolve(pathToTests, 'hermione-transaction-control-plugin');
const htmlReporterPlugin = 'html-reporter/hermione';
const windowSize = {width: 1680, height: 1050};

const disableDownloadShelf = fs
    .readFileSync(path.resolve(__dirname, 'extensions', 'disable-download-shelf.crx').replace('/out', ''))
    .toString('base64');

const config: DeepPartial<Hermione.Config> = {
    sets: {e2e: {files: `${pathToTests}/**/*.hermione.js`}},
    browsers: {
        chrome: {
            desiredCapabilities: {
                browserName: 'chrome',
                browserVersion: '92.0',
                'selenoid:options': {
                    enableVNC: CI ? false : true,
                    enableVideo: false,
                    enableLog: Boolean(E2E_ENABLE_SELENOID_LOG),
                    screenResolution: `${windowSize.width}x${windowSize.height}x24`,
                    hostsEntries: CI ? [] : ['host.docker.internal:host-gateway'],
                    name: 'eagle-e2e'
                },
                'goog:chromeOptions': {
                    args: [
                        '--disable-setuid-sandbox',
                        '--disable-web-security',
                        '--accept-insecure-certificates',
                        '--disable-gpu',
                        `--window-size=${windowSize.width}x${windowSize.height}x24`,
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
    gridUrl: `http://${SELENOID_HOST}/wd/hub`,
    windowSize,
    screenshotDelay: 100,
    tolerance: 2.5,
    antialiasingTolerance: 8,
    screenshotMode: 'viewport',
    assertViewOpts: {allowViewportOverflow: true},
    sessionsPerBrowser: 5,
    testsPerSession: testsPerWorker,
    retry: TEST_RETRY ? Number(TEST_RETRY) : 0,
    testTimeout: TEST_TIMEOUT ? Number(TEST_TIMEOUT) : null,
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
        workers: 7,
        testsPerWorker
    },
    async prepareBrowser(browser: WebdriverIO.Browser) {
        if (E2E_LOG_NETWORK_EVENTS) {
            await enableDevtoolsNetworkPlainWS({
                sessionId: browser.sessionId,
                selenoidHost: SELENOID_HOST,
                logResponseBody: Boolean(E2E_LOG_RESPONSE_BODY)
            });
        }

        browser.addCommand('clickInto', clickInto);
        browser.addCommand('clickIntoEnsured', clickIntoEnsured);
        browser.addCommand('processTaskQueue', processTaskQueue);
        browser.addCommand('typeInto', typeInto);
        browser.addCommand('assertBySelector', assertBySelector);
        browser.addCommand('waitForTestIdSelectorInDom', waitForTestIdSelectorInDom);
        browser.addCommand('waitForTestIdSelectorNotInDom', waitForTestIdSelectorNotInDom);
        browser.addCommand('waitForTestIdSelectorEnabled', waitForTestIdSelectorEnabled);
        browser.addCommand('waitForTestIdSelectorDisabled', waitForTestIdSelectorDisabled);
        browser.addCommand('waitForTestIdSelectorAriaDisabled', waitForTestIdSelectorAriaDisabled);
        browser.addCommand('waitForTestIdSelectorAriaChecked', waitForTestIdSelectorAriaChecked);
        browser.addCommand('waitForTestIdSelectorClickable', waitForTestIdSelectorClickable);
        browser.addCommand('waitForTestIdSelectorNotClickable', waitForTestIdSelectorNotClickable);
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
        browser.addCommand('removeByTestId', removeByTestId);
        browser.addCommand('moveMouseTo', moveMouseTo);
        browser.addCommand('hideBySelector', hideBySelector);
        browser.addCommand('showBySelector', showBySelector);
        browser.addCommand('waitForTestIdSelectorDisplayed', waitForTestIdSelectorDisplayed);
        browser.addCommand('checkForExistenceByTestId', checkForExistenceByTestId);
    }
};

module.exports = config;
