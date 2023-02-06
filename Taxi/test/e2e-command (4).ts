import execa from 'execa';
import {noop} from 'lodash';
import {waitUntilUsed} from 'tcp-port-used';

import {serviceResolve} from '@/src/lib/resolve';
import {handle as startServer} from 'cli/start/server-command';
import {handle as tanker} from 'cli/tanker-command';
import {PATH_TO_HERMIONE_CONFIG} from 'cli/test/constants';
import {writeInfo} from 'cli/test/utils';
import {assertNumericArgument, CliUsage, defaultHelpArg} from 'cli/util';
import {config} from 'service/cfg';
import {assertString} from 'service/helper/assert-string';

export interface HandleInput {
    gui?: boolean;
    paths?: string[];
    test?: string;
    timeout?: string;
    retry?: string;
    update?: boolean;
    ci?: boolean;
    skipTanker?: boolean;
    help?: boolean;
    instances?: number;
    sessions?: number;
    workers?: number;
    vnc?: boolean;
}

export const usage: CliUsage<HandleInput> = {
    parse: {
        gui: {type: Boolean, optional: true, description: 'Запустить графический интерфейс по управлению скриншотами'},
        paths: {type: String, multiple: true, optional: true, alias: 'p'},
        test: {type: String, optional: true, alias: 't'},
        update: {type: Boolean, optional: true, alias: 'u'},
        timeout: {type: String, optional: true},
        retry: {type: String, optional: true},
        ci: {type: Boolean, optional: true, description: 'Флаг запуска в CI цикле'},
        skipTanker: {type: Boolean, optional: true, description: 'Не пулить свежие переводы из танкера'},
        instances: {
            type: Number,
            optional: true,
            description: 'Количество инстансов приложения для старта',
            defaultValue: 1
        },
        sessions: {
            type: Number,
            optional: true,
            description: 'Количество одновременно запущенных сессий браузера',
            defaultValue: 5
        },
        workers: {
            type: Number,
            optional: true,
            description: 'Количество воркеров для выполнения тестов',
            defaultValue: 3
        },
        vnc: {type: Boolean, optional: true, description: 'Запускать VNC для браузера'},
        help: defaultHelpArg
    },
    options: {helpArg: 'help'}
};

const PORT_RETRY_MS = 500;
const PORT_TIMEOUT_MS = 60000;

const SELENOID_PORT = 4444;
const SELENOID_UI_PORT = 8081;
const APP_PORT = 3000;

const HOST_DOCKER_INTERNAL = `http://host.${process.platform === 'darwin' ? 'lima' : 'docker'}.internal`;
const LOCALHOST = 'http://localhost';
const CI_GATEWAY = 'http://172.16.238.1';
const CI_CONTAINER = 'http://172.16.238.4';

export async function handle({
    gui,
    update,
    paths,
    test,
    timeout,
    skipTanker,
    retry,
    ci,
    instances,
    sessions,
    vnc,
    workers
}: HandleInput = {}) {
    assertNumericArgument(instances, {min: 1, integer: true, message: 'Instances number must be positive integer'});
    assertNumericArgument(sessions, {min: 1, integer: true, message: 'Sessions number must be positive integer'});
    assertNumericArgument(workers, {min: 1, integer: true, message: 'Workers number must be positive integer'});

    if (!ci && !skipTanker) {
        await tanker({pull: true});
    }

    const instancesCount = Math.max(instances ?? 0, 1);

    if (ci) {
        await Promise.all(
            assertString(process.env.PG_DATABASE_E2E_TEST)
                .split(',')
                .slice(0, instancesCount)
                .map((dbName) =>
                    execa(
                        serviceResolve('./cli.js'),
                        ['db', 'prepare-db', '--prune', '--migrate', '--seed', '--mockDates', '--ci'],
                        {
                            stdout: 'inherit',
                            stderr: 'inherit',
                            env: {PG_DATABASE: dbName.trim()}
                        }
                    )
                )
        );

        await startServer({ci: true, e2e: true, noReload: true, wait: true, instances});
    }

    if (!ci) {
        await startSelenoid();
    }

    try {
        (['SIGINT', 'SIGTERM'] as NodeJS.Signals[]).forEach((signal) => process.on(signal, noop));
        await executeTests({gui, update, paths, test, timeout, retry, ci, vnc, sessions, workers});
    } finally {
        if (!ci) {
            await stopSelenoid();
        }
    }
}

async function removeDanglingBrowserContainers() {
    const {stdout: containersIds} = await execa('docker', ['ps', '-aqf', 'label=name=pigeon-e2e']);
    if (containersIds) {
        await execa('docker', ['rm', '-f', ...containersIds.split('\n')]).catch(noop);
    }
}

async function startSelenoid() {
    void execa('docker-compose', ['-f', serviceResolve('docker-compose.yaml'), 'up', 'selenoid', 'selenoid-ui'], {
        stderr: 'inherit'
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
            ['-f', serviceResolve('docker-compose.yaml'), 'rm', '-f', '-s', '-v', 'selenoid', 'selenoid-ui'],
            {stderr: 'inherit'}
        ),
        removeDanglingBrowserContainers()
    ]);
}

async function executeTests({
    gui,
    update,
    paths,
    test,
    timeout,
    retry,
    ci,
    vnc,
    sessions,
    workers
}: Partial<HandleInput>) {
    const args = [];

    args.push('--config', PATH_TO_HERMIONE_CONFIG);
    args.push('--reporter', 'plain');

    if (gui) {
        args.push('gui');
    }

    if (test) {
        args.push('--grep', test);
    }

    if (update) {
        args.push('--update-refs');
    }

    if (paths) {
        args.push(...handlePathList(paths));
    }

    writeInfo(`Running tests on ${ci ? CI_CONTAINER : HOST_DOCKER_INTERNAL}:${APP_PORT}`);

    return await execa('npx', [config.cli.hermioneBinary, ...args], {
        stdin: 'inherit',
        stdout: 'inherit',
        stderr: 'inherit',
        env: {
            CI: ci ? '1' : undefined,
            VNC: vnc ? '1' : undefined,
            SELENOID_DOMAIN: `${ci ? CI_GATEWAY : LOCALHOST}:${SELENOID_PORT}`,
            BROWSER_DOMAIN: `${ci ? CI_CONTAINER : HOST_DOCKER_INTERNAL}`,
            TEST_DOMAIN: LOCALHOST,
            TEST_REGION: 'ru',
            TEST_TIMEOUT: timeout,
            TEST_RETRY: retry,
            SESSIONS_PER_BROWSER: String(sessions),
            TEST_WORKERS_COUNT: String(workers),
            ...(update ? {CHAI_SNAPSHOT_UPDATE: '1'} : {})
        }
    });
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
