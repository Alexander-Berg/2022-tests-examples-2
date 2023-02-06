import fs from 'fs';
import path from 'path';
import {remakePublicSchema} from 'tests/unit/util';

import {resolve} from '@/src/lib/resolve';
import {config} from 'service/cfg';
import {ensureDbConnection} from 'service/db';

export default async function () {
    const connection = await ensureDbConnection();

    await remakePublicSchema(connection);

    const root = resolve(config.db.migrationsDir, 'migrations');
    const files = await fs.promises.readdir(root);

    for (const file of files.sort()) {
        const sql = await fs.promises.readFile(path.join(root, file), {encoding: 'utf8'});

        await connection.query(sql);
    }

    await connection.close();
}
