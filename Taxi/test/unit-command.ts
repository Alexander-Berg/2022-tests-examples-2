import execa from 'execa';

import {handle as compileSources} from 'cli/compile/sources-command';
import {startTestDb, stopTestDb} from 'cli/test/utils';
import {CliUsage, defaultHelpArg, resolveFromRoot} from 'cli/util';
import {config} from 'service/cfg';
import {assertString} from 'service/helper/assert-string';
import {checkDbConnection} from 'service/helper/check-db-connection';

export interface HandleInput {
    noCompile?: boolean;
    pathList?: string[];
    grep?: string;
    ci?: boolean;
    help?: boolean;
}

export const usage: CliUsage<HandleInput> = {
    parse: {
        noCompile: {type: Boolean, optional: true, alias: 'C'},
        pathList: {type: String, multiple: true, optional: true, alias: 'p'},
        grep: {
            type: String,
            optional: true,
            alias: 'g',
            description: 'Запустить только тесты с названиями, которые матчатся этой строкой'
        },
        ci: {type: Boolean, optional: true, description: 'Флаг запуска в CI цикле'},
        help: defaultHelpArg
    },
    options: {helpArg: 'help'}
};

export async function handle({noCompile = false, pathList, ci, grep}: HandleInput = {}) {
    if (ci) {
        await checkDbConnection({keepAliveMs: 2000});
    } else if (!noCompile) {
        await compileSources();
    }

    if (!ci) {
        await stopTestDb();
        await startTestDb();
    }

    await makeTest({pathList, grep});

    if (!ci) {
        await stopTestDb();
    }
}

async function makeTest({pathList, grep}: Pick<HandleInput, 'pathList' | 'grep'> = {}) {
    const args = ['--config', resolveFromRoot('./tools/jest/config.unit.js'), '--runInBand'];

    if (grep) {
        args.push(`--testNamePattern=${grep}`);
    }

    args.push(...(Array.isArray(pathList) ? handlePathList(pathList) : []));

    await execa('npx', [config.cli.jestBinary, ...args], {
        stdout: 'inherit',
        stderr: 'inherit',
        env: {
            PG_PORT: process.env.PG_PORT_TEST || process.env.PG_PORT,
            PG_DATABASE: assertString(process.env.PG_DATABASE_TEST, {
                errorMessage: 'Missed "process.env.PG_DATABASE_TEST"!'
            }),
            FORCE_DB_LOG_DISABLE: '1'
        }
    });
}

function handlePathList(pathList: string[]) {
    return pathList.map((path) => path.replace(/\.test\.(js|ts)$/, ''));
}
