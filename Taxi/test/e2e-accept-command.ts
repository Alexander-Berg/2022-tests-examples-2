import execa from 'execa';
import fs from 'fs';
import path from 'path';

import {PATH_TO_HERMIONE_CONFIG, PATH_TO_HERMIONE_HTML_REPORT} from 'cli/test/constants';
import {writeInfo} from 'cli/test/utils';
import {CliUsage, defaultHelpArg} from 'cli/util';
import {config} from 'service/cfg';

export interface HandleInput {
    help?: boolean;
}

export const usage: CliUsage<HandleInput> = {
    parse: {
        help: defaultHelpArg
    },
    options: {helpArg: 'help'}
};

export async function handle() {
    const unpackTo = path.dirname(PATH_TO_HERMIONE_HTML_REPORT);
    const args = ['gui', '--config', PATH_TO_HERMIONE_CONFIG];

    if (fs.existsSync(PATH_TO_HERMIONE_HTML_REPORT)) {
        fs.rmdirSync(PATH_TO_HERMIONE_HTML_REPORT, {recursive: true});
    } else {
        fs.mkdirSync(unpackTo, {recursive: true});
    }
    writeInfo(`Report was downloaded and unpacked into ${PATH_TO_HERMIONE_HTML_REPORT}`);

    return await execa('npx', [config.cli.hermioneBinary, ...args], {
        stdout: 'inherit',
        stderr: 'inherit'
    });
}
