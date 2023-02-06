import got from 'got';
import buildServerUrl from 'tests/e2e/utils/build-server-url';

import {routes} from 'server/middlewares/test';
import {TRANSACTION_UUID_COOKIE} from 'service/transaction-controller/constants';

/**
 * Запускает обработку очереди задач
 */
export async function processTaskQueue(this: WebdriverIO.Browser) {
    const uuid = this.executionContext.uuid;
    await got.get(buildServerUrl(routes.processTaskQueue(), this.executionContext.port), {
        headers: {
            cookie: `${TRANSACTION_UUID_COOKIE}=${uuid}`
        }
    });
}

export type ProcessTaskQueue = typeof processTaskQueue;
