/* eslint-disable @typescript-eslint/no-explicit-any */
import nock from 'nock';
import type {QueryRunner} from 'typeorm';
import {Connection, EntityManager} from 'typeorm';
import {TransactionalTestContext} from 'typeorm-transactional-tests';

import {ensureConnection} from 'service/db';

type RunInTransaction = (entityManager: EntityManager) => Promise<any>;

let connection: Connection;
let transactionalContext: TransactionalTestContext;
let queryRunner: QueryRunner;
let originalCreateQueryRunner: Connection['createQueryRunner'];
let originalTransaction: EntityManager['transaction'];

export async function createUnPatchedQueryRunner() {
    const unPatchedQueryRunner = await originalCreateQueryRunner.call(connection);
    unPatchedQueryRunner.manager.transaction = originalTransaction;
    return unPatchedQueryRunner;
}

beforeEach(async () => {
    connection = await ensureConnection();
    transactionalContext = new TransactionalTestContext(connection);
    await transactionalContext.start();
    queryRunner = connection.createQueryRunner();

    // Каждый тест запускается в транзакции
    // Запустить транзакцию в транзакции нельзя
    // Для того чтобы тестировать методы которые вызывают транзакции, нужно прокидывать текущую транзакцию теста
    (EntityManager.prototype.transaction as any) = async (runInTransaction: RunInTransaction) => {
        return await runInTransaction(queryRunner.manager);
    };
});

afterEach(async () => {
    nock.cleanAll();
    // Если откатили транзакцию до завершения теста, то нужно запустить её заново
    if (!queryRunner.isTransactionActive) {
        await queryRunner.startTransaction();
    }
    await transactionalContext.finish();
});

beforeAll(async () => {
    originalCreateQueryRunner = Connection.prototype.createQueryRunner;
    originalTransaction = EntityManager.prototype.transaction;

    nock.disableNetConnect();
    nock.enableNetConnect(/localhost/);
});

afterAll(async () => {
    nock.enableNetConnect();
    await connection.close();
});
