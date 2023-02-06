import {existsSync, promises as fs} from 'fs';
import path from 'path';

import {CliUsage, defaultHelpArg} from 'cli/util';
import type {ReadOnlySecrets} from 'config/db';
import {config} from 'service/cfg';
import {dump, roll} from 'service/db/dump-utils';

interface HandleInput {
    refresh?: boolean;
    noHistoryData?: boolean;
    help?: boolean;
}

type DbCredentials = {
    host: [string, ...string[]];
    port: number;
    dbname: string;
    user: string;
    password: string;
};

export const usage: CliUsage<HandleInput> = {
    parse: {
        refresh: {
            type: Boolean,
            optional: true,
            description: 'Скачать свежий дамп базы',
            alias: 'r'
        },
        noHistoryData: {
            type: Boolean,
            optional: true,
            description: 'Не скачивать данные истории'
        },
        help: defaultHelpArg
    },
    options: {helpArg: 'help'}
};

export async function handle({refresh, noHistoryData}: HandleInput = {}) {
    const destFile = path.join(config.app.tmpDir, config.db.dumpFilename);
    const exists = existsSync(destFile);

    if (!exists || refresh) {
        const credentials = await extractCredentials();

        const extraCommands = noHistoryData ? ['--exclude-table-data=history'] : [];
        await dump(credentials, destFile, extraCommands);
        console.log(`Dump has been downloaded to "${destFile}"`);
    }

    try {
        await roll(destFile, ['--section=pre-data']);
    } catch {
        console.log('Schema may already have been applied');
    }
    await roll(destFile);
}

async function extractCredentials(): Promise<ReadOnlySecrets> {
    const {rootDir} = cliRuntime();

    const credentials = JSON.parse(
        (await fs.readFile(path.join(rootDir, '.dev', 'db.testing.json'))).toString()
    ) as DbCredentials;

    return {
        user: credentials.user,
        password: credentials.password,
        port: String(credentials.port),
        host: credentials.host[0],
        database: credentials.dbname
    };
}
