import execa from 'execa';
import {existsSync, promises as fs} from 'fs';
import path from 'path';

import {CliUsage, defaultHelpArg} from 'cli/util';
import {config} from 'service/cfg';

interface HandleInput {
    refresh?: boolean;
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
        help: defaultHelpArg
    },
    options: {helpArg: 'help'}
};

const DUMP_FILE = 'eagle_testing_db.dump';

export async function handle({refresh}: HandleInput = {}) {
    const dumpFile = path.join(config.app.tmpDir, DUMP_FILE);
    const exists = existsSync(dumpFile);

    if (!exists || refresh) {
        await dump(dumpFile);
    }

    await roll(dumpFile);
}

async function dump(dest: string) {
    const {rootDir} = cliRuntime();
    const {host, port, user, password, dbname} = JSON.parse(
        (await fs.readFile(path.join(rootDir, '.dev', 'db.testing.json'))).toString()
    ) as DbCredentials;

    const args = ['--format=c', '--no-owner', '--no-privileges', '--lock-wait-timeout=5s', '--clean'].join(' ');

    await execa('bash', ['-c', `pg_dump ${args} > ${dest}`], {
        stdout: 'inherit',
        stderr: 'inherit',
        env: {
            PGHOST: host[0],
            PGPORT: String(port),
            PGUSER: user,
            PGPASSWORD: password,
            PGDATABASE: dbname,
            PGSSLMODE: 'allow'
        }
    });
}

async function roll(source: string) {
    await rollSchema(source);

    const args = [
        '--data-only',
        `--superuser=${config.db.user}`,
        '--disable-triggers',
        '--single-transaction',
        '--no-owner',
        '--no-privileges',
        `-d ${config.db.database}`
    ].join(' ');

    await execa('bash', ['-c', `pg_restore ${args} ${source}`], {
        stdout: 'inherit',
        stderr: 'inherit',
        env: {
            PGHOST: config.db.masterHost,
            PGPORT: String(config.db.port),
            PGUSER: config.db.user,
            PGPASSWORD: config.db.password
        }
    });
}

async function rollSchema(source: string) {
    const args = [
        '--clean',
        '--if-exists',
        '--schema-only',
        `--superuser=${config.db.user}`,
        '--exit-on-error',
        '--no-owner',
        '--no-privileges',
        `-d ${config.db.database}`
    ].join(' ');

    await execa('bash', ['-c', `pg_restore ${args} ${source}`], {
        stdout: 'inherit',
        stderr: 'inherit',
        env: {
            PGHOST: config.db.masterHost,
            PGPORT: String(config.db.port),
            PGUSER: config.db.user,
            PGPASSWORD: config.db.password
        }
    });
}
