import execa from 'execa';

import {serviceResolve} from '@/src/lib/resolve';
import {handle as babel} from 'cli/compile/babel-command';
import {CliUsage, defaultHelpArg} from 'cli/util';
import {config} from 'service/cfg';
import {assertString} from 'service/helper/assert-string';
import {checkDbConnection} from 'service/helper/check-db-connection';

export interface HandleInput {
    noCompile?: boolean;
    pathList?: string[];
    ci?: boolean;
    help?: boolean;
}

export const usage: CliUsage<HandleInput> = {
    parse: {
        noCompile: {type: Boolean, optional: true, alias: 'C'},
        pathList: {type: String, multiple: true, optional: true, alias: 'p'},
        ci: {type: Boolean, optional: true, description: 'Флаг запуска в CI цикле'},
        help: defaultHelpArg
    },
    options: {helpArg: 'help'}
};

export async function handle({noCompile = false, pathList, ci}: HandleInput = {}) {
    if (ci) {
        await checkDbConnection({keepAliveMs: 2000});
    } else if (!noCompile) {
        await babel();
    }

    await makeTest({pathList});
}

async function makeTest({pathList}: Pick<HandleInput, 'pathList' | 'ci'> = {}) {
    const args = ['--config', serviceResolve('./tools/jest/config.unit.js'), '--maxWorkers', '7'];

    args.push(...(Array.isArray(pathList) ? handlePathList(pathList) : []));

    await execa('npx', [config.cli.jestBinary, ...args], {
        stdout: 'inherit',
        stderr: 'inherit',
        env: {
            PG_DATABASE: assertString(process.env.PG_DATABASE_UNIT_TEST, {
                errorMessage: 'Missed "process.env.PG_DATABASE_UNIT_TEST"!'
            }),
            FORCE_DB_LOG_DISABLE: '1'
        }
    });
}

export function handlePathList(pathList: string[]) {
    return pathList.map((path) => path.replace(/\.test\.(js|ts)$/, ''));
}
