import execa from 'execa';
import fs from 'fs';
import {noop} from 'lodash';
import {waitUntilUsed} from 'tcp-port-used';
import restoreDb from 'tests/unit/restore-db';

import {resolve, rootResolve} from '@/src/lib/resolve';
import {handle as seedDb} from 'cli/db/seed-command';
import {handle as startServer} from 'cli/start/server-command';
import {PATH_TO_HERMIONE_CONFIG, PATH_TO_HERMIONE_HTML_REPORT} from 'cli/test/constants';
import {writeInfo} from 'cli/test/utils';
import {CliUsage, defaultHelpArg, resolveFromRoot} from 'cli/util';
import {config} from 'service/cfg';
import {FILE_WRITER_DEST} from 'service/logger';

export interface HandleInput {
    gui?: boolean;
    paths?: string[];
    grep?: string;
    timeout?: string;
    retry?: string;
    update?: boolean;
    ci?: boolean;
    skipTanker?: boolean;
    logNetworkEvents?: boolean;
    logResponseBody?: boolean;
    enableSelenoidLog?: boolean;
    help?: boolean;
}

export const usage: CliUsage<HandleInput> = {
    parse: {
        gui: {type: Boolean, optional: true, description: 'Запустить графический интерфейс по управлению скриншотами'},
        paths: {type: String, multiple: true, optional: true, alias: 'p'},
        grep: {
            type: String,
            optional: true,
            alias: 'g',
            description: 'Запустить тесты, названия которых матчатся со такой строкой'
        },
        update: {type: Boolean, optional: true, alias: 'u'},
        timeout: {type: String, optional: true},
        retry: {type: String, optional: true, defaultValue: '3'},
        ci: {type: Boolean, optional: true, description: 'Флаг запуска в CI цикле'},
        skipTanker: {type: Boolean, optional: true, description: 'Не пулить свежие переводы из танкера'},
        logNetworkEvents: {type: Boolean, optional: true, description: 'Логировать сетевые события в браузере'},
        logResponseBody: {type: Boolean, optional: true, description: 'Логировать тело ответа запросов в браузере'},
        enableSelenoidLog: {type: Boolean, optional: true, description: 'Показывать логи селеноида'},
        help: defaultHelpArg
    },
    options: {helpArg: 'help'}
};

const PORT_RETRY_MS = 500;
const PORT_TIMEOUT_MS = 60000;

const SELENOID_PORT = 4444;
const SELENOID_UI_PORT = 8081;
const APP_PORT = 3000;

const DOCKER_INTERNAL_HOSTNAME = `host.${process.platform === 'darwin' ? 'lima' : 'docker'}.internal`;
const LOCAL_HOSTNAME = 'localhost';
const CI_GATEWAY_HOSTNAME = '172.16.238.1';
const CI_CONTAINER_HOSTNAME = '172.16.238.4';

export async function handle(options: HandleInput = {}) {
    if (options.ci) {
        await restoreDb();
        await seedDb({mockDates: true});
        await startServer({ci: true});
        await waitUntilUsed(config.server.port, PORT_RETRY_MS, PORT_TIMEOUT_MS);
    }

    if (!options.ci) {
        await startSelenoid({forwardStdout: options.enableSelenoidLog});
    }

    try {
        ['SIGINT', 'SIGTERM'].forEach((signal) => process.on(signal, noop));
        await executeTests(options);
    } finally {
        if (!options.ci) {
            await stopSelenoid();
        }
    }
}

async function removeDanglingBrowserContainers() {
    const {stdout: containersIds} = await execa('docker', ['ps', '-aqf', 'label=name=eagle-e2e']);
    if (containersIds) {
        await execa('docker', ['rm', '-f', ...containersIds.split('\n')]).catch(noop);
    }
}

interface StartSelenoidOptions {
    forwardStdout?: boolean;
}

async function startSelenoid({forwardStdout}: StartSelenoidOptions = {}) {
    void execa('docker-compose', ['-f', resolveFromRoot('docker-compose.yaml'), 'up', 'selenoid', 'selenoid-ui'], {
        stderr: 'inherit',
        ...(forwardStdout ? {stdout: 'inherit'} : {})
    });

    await Promise.all([
        removeDanglingBrowserContainers(),
        waitUntilUsed(SELENOID_PORT, PORT_RETRY_MS, PORT_TIMEOUT_MS),
        waitUntilUsed(SELENOID_UI_PORT, PORT_RETRY_MS, PORT_TIMEOUT_MS)
    ]);
}

async function stopSelenoid() {
    await Promise.all([
        execa(
            'docker-compose',
            ['-f', resolveFromRoot('docker-compose.yaml'), 'rm', '-f', '-s', '-v', 'selenoid', 'selenoid-ui'],
            {stderr: 'inherit'}
        ),
        removeDanglingBrowserContainers()
    ]);
}

async function executeTests({
    gui,
    update,
    paths,
    grep,
    timeout,
    retry,
    ci,
    logNetworkEvents,
    logResponseBody,
    enableSelenoidLog
}: Partial<HandleInput>) {
    const args = [];

    args.push('--config', PATH_TO_HERMIONE_CONFIG);
    args.push('--reporter', 'plain');

    if (gui) {
        args.push('gui');
    }

    if (grep) {
        args.push('--grep', grep);
    }

    if (update) {
        args.push('--update-refs');
    }

    if (paths) {
        args.push(...handlePathList(paths));
    }

    writeInfo(`Running tests on ${ci ? CI_CONTAINER_HOSTNAME : DOCKER_INTERNAL_HOSTNAME}:${APP_PORT}`);

    try {
        await execa('npx', [config.cli.hermioneBinary, ...args], {
            stdin: 'inherit',
            stdout: 'inherit',
            stderr: 'inherit',
            env: {
                CI: ci ? '1' : undefined,
                SELENOID_HOST: `${ci ? CI_GATEWAY_HOSTNAME : LOCAL_HOSTNAME}:${SELENOID_PORT}`,
                BROWSER_HOST: `${ci ? CI_CONTAINER_HOSTNAME : DOCKER_INTERNAL_HOSTNAME}:${APP_PORT}`,
                TEST_HOST: `${LOCAL_HOSTNAME}:${APP_PORT}`,
                TEST_REGION: 'ru',
                TEST_TIMEOUT: timeout,
                TEST_RETRY: retry,
                ...(update ? {CHAI_SNAPSHOT_UPDATE: '1'} : {}),
                ...(logNetworkEvents ? {E2E_LOG_NETWORK_EVENTS: '1'} : {}),
                ...(logResponseBody ? {E2E_LOG_RESPONSE_BODY: '1'} : {}),
                ...(enableSelenoidLog ? {E2E_ENABLE_SELENOID_LOG: '1'} : {})
            }
        });
    } finally {
        await fs.promises.copyFile(rootResolve(FILE_WRITER_DEST), resolve(PATH_TO_HERMIONE_HTML_REPORT, 'taxi.log'));
    }
}

export function handlePathList(pathList: string[]) {
    return pathList.map((path) => {
        const normalizedExtensionPath = path.replace(/\.(js|ts)$/, '.js');
        if (normalizedExtensionPath.startsWith('out')) {
            return normalizedExtensionPath;
        } else {
            return `out/${normalizedExtensionPath}`;
        }
    });
}
