import {CliUsage, defaultHelpArg} from '@lavka-js-toolbox/cli';
import execa from 'execa';

import {BIN_LERNA} from './util';

interface HandleInput {
    help?: boolean;
}

export const usage: CliUsage<HandleInput> = {
    parse: {
        help: defaultHelpArg
    },
    options: {
        helpArg: 'help',
        headerContentSections: [{content: 'Test packages'}]
    }
};

export async function handle(_: HandleInput = {}) {
    await execa(BIN_LERNA, ['run', '--stream', 'test', '--', '--', '--noCompile'], {
        stdout: 'inherit',
        stderr: 'inherit'
    });
}
