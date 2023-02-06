import {CliUsage, defaultHelpArg} from '@lavka-js-toolbox/cli';
import execa from 'execa';

import {BIN_JEST} from '../util';
import {handle as compile} from './compile-command';
import {handleNameOrInitCwd} from './util';

interface HandleInput {
    name: string;
    noCompile?: boolean;
    detectOpenHandles?: boolean;
    help?: boolean;
}

export const usage: CliUsage<HandleInput> = {
    parse: {
        name: {type: String, description: 'Package name OR lerna ${INIT_CWD} value'},
        noCompile: {type: Boolean, optional: true, alias: 'C', description: 'Skip package compilation'},
        detectOpenHandles: {type: Boolean, optional: true, description: 'Detect open handles in tests'},
        help: defaultHelpArg
    },
    options: {
        helpArg: 'help',
        headerContentSections: [{content: 'Test specified package'}]
    }
};

export async function handle({name, noCompile, detectOpenHandles}: HandleInput) {
    const cwd = handleNameOrInitCwd(name);

    if (!noCompile) {
        await compile({name});
    }

    const args = ['--maxWorkers', '7', '--passWithNoTests'];

    if (detectOpenHandles) {
        args.push('--detectOpenHandles');
    }

    await execa(BIN_JEST, args, {
        cwd,
        stdout: 'inherit',
        stderr: 'inherit',
        env: {
            NODE_ENV: 'test'
        }
    });
}
