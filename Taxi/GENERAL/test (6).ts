import express, {Request, Response} from 'express';
import {isPlainObject} from 'lodash';
import {v4 as uuidv4} from 'uuid';

import {UnknownError} from '@/src/errors';
import {ensureConnection, HISTORY_AUTHOR_ID, HISTORY_SOURCE, HISTORY_STAMP} from 'service/db';
import {asyncMiddleware} from 'service/express/async-middleware';
import {USER_LOGIN} from 'service/seed-db/fixtures';
import {processTaskQueue} from 'service/task-queue';

export const routes = {
    processTaskQueue: () => '/test/process-task-queue',
    executeSql: () => '/test/execute-sql',
    serverError: () => '/test/server-error'
} as const;

export function testMiddleware() {
    const router = express.Router();

    router.get(
        routes.serverError(),
        asyncMiddleware(async (_req: Request, _res: Response) => {
            throw new UnknownError();
        })
    );

    router.get(
        routes.processTaskQueue(),
        asyncMiddleware(async (_req: Request, res: Response) => {
            await processTaskQueue();
            res.sendStatus(200);
        })
    );

    router.post(
        routes.executeSql(),
        asyncMiddleware(async (req: Request, res: Response) => {
            const connection = await ensureConnection();

            const sql = req.body.sql;
            const parameters = req.body.parameters;

            const queryResult = await connection.transaction(async (manager) => {
                await manager.query(`
                    WITH author AS (SELECT id AS author_id FROM "user" WHERE login = '${USER_LOGIN}')
                    SELECT
                        set_config('${HISTORY_AUTHOR_ID}', (
                            SELECT CAST(id AS text) FROM "user" WHERE login = '${USER_LOGIN}'
                        ), TRUE),
                        set_config('${HISTORY_SOURCE}', 'manual', TRUE),
                        set_config('${HISTORY_STAMP}', '${uuidv4()}', TRUE);
                `);
                return manager.query(sql, parameters);
            });

            if (Array.isArray(queryResult) || isPlainObject(queryResult)) {
                res.json(queryResult);
            } else {
                res.sendStatus(200);
            }
        })
    );

    return router;
}
