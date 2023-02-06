import execa from 'execa';
import kleur from 'kleur';
import {noop} from 'lodash';
import {waitUntilUsed} from 'tcp-port-used';

import {resolveFromRoot} from 'cli/util';
import {CheckConnectionInput, checkDbConnection} from 'service/helper/check-db-connection';

const SELENOID_UI_PORT = 8081;
export const SELENOID_PORT = 4444;
export const PORT_RETRY_MS = 500;
export const PORT_TIMEOUT_MS = 60000;

export function writeInfo(msg: string) {
    return console.log(kleur.cyan().bold(msg));
}

async function removeDanglingBrowserContainers() {
    const {stdout: containersIds} = await execa('docker', ['ps', '-aqf', 'label=name=eagle-e2e']);
    if (containersIds) {
        await execa('docker', ['rm', '-f', ...containersIds.split('\n')]);
    }
}

export async function startSelenoid() {
    void execa('docker-compose', ['-f', resolveFromRoot('docker-compose.yaml'), 'up', 'selenoid', 'selenoid-ui'], {
        stderr: 'inherit'
    });

    await Promise.all([
        removeDanglingBrowserContainers(),
        waitUntilUsed(SELENOID_PORT, PORT_RETRY_MS, PORT_TIMEOUT_MS),
        waitUntilUsed(SELENOID_UI_PORT, PORT_RETRY_MS, PORT_TIMEOUT_MS)
    ]);
}

export async function startTestDb(checkConnectionParams: CheckConnectionInput = {}) {
    void execa('docker-compose', ['-f', resolveFromRoot('docker-compose.yaml'), 'up', 'test_db'], {stderr: 'inherit'});

    await checkDbConnection({
        pgPort: Number(process.env.PG_PORT_TEST),
        retryLimit: 20,
        ...checkConnectionParams
    });
}

export async function stopTestDb() {
    await execa('docker-compose', ['-f', resolveFromRoot('docker-compose.yaml'), 'rm', '-f', '-s', '-v', 'test_db'], {
        stderr: 'inherit'
    }).catch(noop);
}

export async function stopSelenoid() {
    await Promise.all([
        execa(
            'docker-compose',
            ['-f', resolveFromRoot('docker-compose.yaml'), 'rm', '-f', '-s', '-v', 'selenoid', 'selenoid-ui'],
            {stderr: 'inherit'}
        ),
        removeDanglingBrowserContainers()
    ]);
}
