import execa from 'execa';

import {serviceResolve} from '@/src/lib/resolve';
import {handle as compileSources} from 'cli/compile/sources-command';
import {CliUsage, defaultHelpArg} from 'cli/util';
import {config} from 'service/cfg';
import {assertString} from 'service/helper/assert-string';
import {checkDbConnection} from 'service/helper/check-db-connection';

export interface HandleInput {
    pathList?: string[];
    ci?: boolean;
    help?: boolean;
}

export const usage: CliUsage<HandleInput> = {
    parse: {
        pathList: {type: String, multiple: true, optional: true, alias: 'p'},
        ci: {type: Boolean, optional: true, description: 'Флаг запуска в CI цикле'},
        help: defaultHelpArg
    },
    options: {helpArg: 'help'}
};

export async function handle({pathList, ci}: HandleInput = {}) {
    if (ci) {
        await checkDbConnection({keepAliveMs: 2000});
    } else {
        await compileSources();
    }

    await makeTest({pathList});
}

async function makeTest({pathList}: Pick<HandleInput, 'pathList'> = {}) {
    const args = ['--config', serviceResolve('./tools/jest/config.unit.js'), '--forceExit'];

    args.push(...(Array.isArray(pathList) ? handlePathList(pathList) : []));

    await execa('npx', [config.cli.jestBinary, ...args], {
        stdout: 'inherit',
        stderr: 'inherit',
        env: {
            NODE_ENV: 'testing',
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
