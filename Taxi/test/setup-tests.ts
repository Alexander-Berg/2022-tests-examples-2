import type {Connection} from 'typeorm';
import {TransactionalTestContext} from 'typeorm-transactional-tests';

import {ensureConnection} from 'service/db';

let connection: Connection;
let transactionalContext: TransactionalTestContext;

beforeEach(async () => {
    connection = await ensureConnection();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    transactionalContext = new TransactionalTestContext((connection as unknown) as any);
    await transactionalContext.start();
});

afterEach(async () => {
    await transactionalContext.finish();
});

afterAll(async () => {
    await connection.close();
});
