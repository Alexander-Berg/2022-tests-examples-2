import got from 'got';
import buildServerUrl from 'tests/e2e/utils/build-server-url';

import {routes} from 'server/middlewares/test';
import {TRANSACTION_UUID_COOKIE} from 'service/transaction-controller/constants';

/**
 * Исполняет SQL в рамках транзакции теста и возвращает результат
 */
export async function executeSql<T>(this: WebdriverIO.Browser, sql: string, parameters?: unknown[]): Promise<T> {
    const uuid = this.executionContext.uuid;
    const {body} = await got.post(buildServerUrl(routes.executeSql(), this.executionContext.port), {
        json: {sql, parameters},
        headers: {
            cookie: `${TRANSACTION_UUID_COOKIE}=${uuid}`
        }
    });
    return JSON.parse(body);
}

export type ExecuteSql = typeof executeSql;
