import got from 'got';
import {buildTestUrl} from 'tests/e2e/utils/build-test-url';

import {routes} from 'server/middlewares/test';
import {TRANSACTION_UUID_COOKIE} from 'service/transaction-controller/constants';

/**
 * Исполняет SQL в рамках транзакции теста и возвращает результат
 */
export async function executeSql<T>(this: WebdriverIO.Browser, sql: string, parameters?: unknown[]): Promise<T> {
    const uuid = this.executionContext.uuid;
    const {body} = await got.post(buildTestUrl(routes.executeSql()), {
        json: {sql, parameters},
        headers: {
            cookie: `${TRANSACTION_UUID_COOKIE}=${uuid}`
        }
    });
    return JSON.parse(body);
}

export type ExecuteSql = typeof executeSql;
