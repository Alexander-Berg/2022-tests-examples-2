import {configureToMatchImageSnapshot} from 'jest-image-snapshot';

import {toSaveImage} from './commands/assert-image';
import {closeBrowser, openBrowser} from './commands/open-browser';

import 'pptr-testing-library/extend';

const toMatchImageSnapshot = configureToMatchImageSnapshot({
    customDiffDir: './src/tests/__diff__'
});

expect.extend({toMatchImageSnapshot, toSaveImage});

beforeAll(async () => {
    await openBrowser();
});

afterAll(async () => {
    await closeBrowser();
});

const DEFAULT_TEST_TIMEOUT = 30_000;
const timeout = Number(process.env.TEST_TIMEOUT) || DEFAULT_TEST_TIMEOUT;
const DEFAULT_RETRY_TIMEOUT = 3;
const retry = Number(process.env.TEST_RETRY) || DEFAULT_RETRY_TIMEOUT;

jest.setTimeout(timeout);
jest.retryTimes(retry);
