import express, {Request, Response} from 'express';
import {isPlainObject} from 'lodash';

import {ensureDbConnection} from 'service/db';
import {asyncMiddleware} from 'service/express/async-middleware';

export const routes = {
    processTaskQueue: () => '/test/process-task-queue',
    executeSql: () => '/test/execute-sql'
} as const;

export function makeTestMiddleware() {
    const router = express.Router();

    router.get(
        routes.processTaskQueue(),
        asyncMiddleware(async (_req: Request, res: Response) => {
            res.sendStatus(200);
        })
    );

    router.post(
        routes.executeSql(),
        asyncMiddleware(async (req: Request, res: Response) => {
            const {manager} = await ensureDbConnection();
            const sql = req.body.sql;
            const parameters = req.body.parameters;
            const queryResult = await manager.query(sql, parameters);
            if (Array.isArray(queryResult) || isPlainObject(queryResult)) {
                res.json(queryResult);
            } else {
                res.sendStatus(200);
            }
        })
    );

    return router;
}
