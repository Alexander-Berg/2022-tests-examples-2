import {applyMigrations, pruneDatabase} from 'tests/utils';

import {ensureConnection} from 'service/db';

export default async function () {
    const connection = await ensureConnection();

    await pruneDatabase(connection);
    await applyMigrations(connection);

    await connection.close();
}
