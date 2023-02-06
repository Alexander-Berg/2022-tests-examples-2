import fs from 'fs';
import path from 'path';

import {serviceResolve} from '@/src/lib/resolve';
import {config} from 'service/cfg';
import {ensureConnection} from 'service/db';

export default async function () {
    const connection = await ensureConnection();

    await connection.query(`
        DROP SCHEMA IF EXISTS public CASCADE;
        CREATE SCHEMA public;

        CREATE EXTENSION LTREE;
        CREATE EXTENSION HSTORE;
        CREATE EXTENSION PG_TRGM;
    `);

    const root = serviceResolve(config.db.migrationsDir, 'migrations');
    const files = await fs.promises.readdir(root);

    for (const file of files.sort()) {
        const sql = await fs.promises.readFile(path.join(root, file), 'utf-8');

        await connection.query(sql);
    }

    await connection.close();
}
