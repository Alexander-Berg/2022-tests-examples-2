import {uuid} from 'casual';
import {describe, expect, it} from 'tests/jest.globals';

import {Lang} from '@/src/entities/lang/entity';
import {ensureConnection, executeInTransaction} from '@/src/service/db';
import {TestFactory} from '@/src/tests/unit/test-factory';

describe('test database', () => {
    it('should connect successfully', async () => {
        const connection = await ensureConnection();
        const repository = connection.getRepository(Lang);

        await repository.insert({isoCode: Math.random().toString()});
        await expect(repository.count()).resolves.toBeGreaterThan(0);
    });

    it('should set special variables in transaction', async () => {
        const connection = await ensureConnection();

        const authorBefore = await connection.query("SELECT current_setting('history.author_id', TRUE)");
        const stampBefore = await connection.query("SELECT current_setting('history.stamp', TRUE)");
        const sourceBefore = await connection.query("SELECT current_setting('history.source', TRUE)");

        expect(authorBefore).toMatchObject([{current_setting: null}]);
        expect(sourceBefore).toMatchObject([{current_setting: null}]);
        expect(stampBefore).toMatchObject([{current_setting: null}]);

        const user = await TestFactory.createUser();
        const uuidStamp = uuid;

        await executeInTransaction({source: 'ui', stamp: uuidStamp, authorId: user.id}, async (manager) => {
            const author = await manager.query("SELECT current_setting('history.author_id', TRUE)");
            const stamp = await manager.query("SELECT current_setting('history.stamp', TRUE)");
            const source = await manager.query("SELECT current_setting('history.source', TRUE)");

            expect(author).toMatchObject([{current_setting: user.id.toString()}]);
            expect(stamp).toMatchObject([{current_setting: uuidStamp}]);
            expect(source).toMatchObject([{current_setting: 'ui'}]);
        });
    });

    it('should clear variable after transaction was finised', async () => {
        const connection = await ensureConnection();

        const author = await connection.query("SELECT current_setting('history.author_id', TRUE)");
        const stamp = await connection.query("SELECT current_setting('history.stamp', TRUE)");
        const source = await connection.query("SELECT current_setting('history.source', TRUE)");

        expect(author).toMatchObject([{current_setting: ''}]);
        expect(stamp).toMatchObject([{current_setting: ''}]);
        expect(source).toMatchObject([{current_setting: ''}]);
    });
});
