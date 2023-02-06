import {promises as fs} from 'fs';
import path from 'path';
import type {Connection} from 'typeorm';

import {serviceResolve} from '@/src/lib/resolve';
import {config} from 'service/cfg';

export async function pruneDatabase(connection: Connection) {
    for (const sql of [
        'DROP SCHEMA IF EXISTS public CASCADE',
        'DROP SCHEMA IF EXISTS catalog CASCADE',
        'CREATE SCHEMA public',
        'CREATE EXTENSION LTREE',
        'CREATE EXTENSION HSTORE',
        'CREATE EXTENSION PG_TRGM',
        'CREATE EXTENSION "uuid-ossp"'
    ]) {
        await connection.query(sql);
    }
}

export async function applyMigrations(connection: Connection) {
    const root = serviceResolve(config.db.migrationsDir, 'migrations');
    const files = await fs.readdir(root);

    const getMigrationNumber = (fileName: string) => Number(fileName.split('__').shift()?.replace('V', '') || 0);
    const sorted = files.sort((a, b) => getMigrationNumber(a) - getMigrationNumber(b));

    for (const file of sorted) {
        const sql = await fs.readFile(path.join(root, file), {encoding: 'utf8'});

        await connection.query(sql);
    }
}
