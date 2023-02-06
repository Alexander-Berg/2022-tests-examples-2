import got from 'got';
import {buildTestUrl} from 'tests/e2e/utils/build-test-url';

import {routes} from 'server/middlewares/test';
import {TRANSACTION_UUID_COOKIE} from 'service/transaction-controller/constants';

/**
 * Запускает обработку очереди задач
 */
export async function processTaskQueue(this: WebdriverIO.Browser) {
    const uuid = this.executionContext.uuid;
    await got.get(buildTestUrl(routes.processTaskQueue()), {
        headers: {
            cookie: `${TRANSACTION_UUID_COOKIE}=${uuid}`
        }
    });
}

export type ProcessTaskQueue = typeof processTaskQueue;
