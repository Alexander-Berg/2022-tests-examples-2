import {applyMigrations, pruneDatabase} from 'tests/utils';

import {DbTable} from '@/src/entities/const';
import {ensureConnection} from 'service/db';

export default async function () {
    const connection = await ensureConnection();

    await pruneDatabase(connection);
    await applyMigrations(connection);
    // Для избежания deadlock в тестах
    await connection.query(`ALTER TABLE IF EXISTS ${DbTable.LANG} DROP CONSTRAINT IF EXISTS uq__lang__iso_code`);

    await connection.close();
}
