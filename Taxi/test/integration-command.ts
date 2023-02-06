import execa from 'execa';

import {serviceResolve} from '@/src/lib/resolve';
import {handle as compileSources} from 'cli/compile/sources-command';
import {CliUsage, defaultHelpArg} from 'cli/util';
import {config} from 'service/cfg';
import {assertString} from 'service/helper/assert-string';

export interface HandleInput {
    pathList?: string[];
    help?: boolean;
}

export const usage: CliUsage<HandleInput> = {
    parse: {
        pathList: {type: String, multiple: true, optional: true, alias: 'p'},
        help: defaultHelpArg
    },
    options: {helpArg: 'help'}
};

export async function handle({pathList}: HandleInput = {}) {
    await compileSources();

    await makeTest({pathList});
}

async function makeTest({pathList}: Pick<HandleInput, 'pathList'> = {}) {
    const args = ['--config', serviceResolve('./tools/jest/config.integration.js'), '--forceExit', '--runInBand'];

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
    return pathList.map((path) => path.replace(/\.test.integration\.(js|ts)$/, ''));
}
