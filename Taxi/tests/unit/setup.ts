/* eslint-disable @typescript-eslint/no-explicit-any */
import nock from 'nock';
import type {Connection} from 'typeorm';
import {EntityManager} from 'typeorm';
import {TransactionalTestContext} from 'typeorm-transactional-tests';

import {ensureDbConnection} from 'service/db';

type RunInTransaction = (entityManager: EntityManager) => Promise<any>;

let connection: Connection;
let transactionalContext: TransactionalTestContext;

beforeEach(async () => {
    connection = await ensureDbConnection();
    transactionalContext = new TransactionalTestContext(connection);
    await transactionalContext.start();

    // Каждый тест запускается в транзакции
    // Запустить транзакцию в транзакции нельзя
    // Для того чтобы тестировать методы которые вызывают транзакции, нужно прокидывать текущую транзакцию теста
    (EntityManager.prototype.transaction as any) = async (runInTransaction: RunInTransaction) => {
        return await runInTransaction(connection.createQueryRunner().manager);
    };
});

afterEach(async () => {
    nock.cleanAll();
    await transactionalContext.finish();
});

beforeAll(async () => {
    nock.disableNetConnect();
    nock.enableNetConnect(/localhost/);
});

afterAll(async () => {
    nock.enableNetConnect();
    await connection.close();
});
