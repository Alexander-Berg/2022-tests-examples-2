import execa from 'execa';
import glob from 'fast-glob';
import {promises as fs} from 'fs-extra';
import kleur from 'kleur';
import {waitUntilUsed} from 'tcp-port-used';

import {rootResolve, serviceResolve} from '@/src/lib/resolve';
import {CliUsage, defaultHelpArg} from 'cli/util';
import {config} from 'service/cfg';

export interface HandleInput {
    pathList?: string[];
    timeout?: string;
    retry?: string;
    update?: boolean;
    env?: string;
    help?: boolean;
}

export const usage: CliUsage<HandleInput> = {
    parse: {
        pathList: {type: String, multiple: true, optional: true, alias: 'p'},
        update: {type: Boolean, optional: true, alias: 'u'},
        env: {type: String, optional: true, defaultValue: 'dev'},
        timeout: {type: String, optional: true},
        retry: {type: String, optional: true},
        help: defaultHelpArg
    },
    options: {helpArg: 'help'}
};

const EXPECTED_SCREENS_DIR = rootResolve('./reports/.dev/.reg/expected');
const TEMP_SCREENS_DIR = serviceResolve('./tests/actual');

const CHROMIUM_PORT = 9222;
const PORT_RETRY_MS = 500;
const PORT_TIMEOUT_MS = 15000;

const TESTING_DOMAIN = 'https://pim.tst.lavka.yandex-team.ru/ru';
const DEV_DOMAIN = 'https://host.docker.internal:3000/ru';

export async function handle({update, pathList, env, timeout}: HandleInput = {}) {
    let testError;

    // Собираем эталонные скриншоты для отчета
    await screenshotWalk(EXPECTED_SCREENS_DIR);

    // Копируем эталоны в 'actual', чтобы jest-image-snapshot сравнивал с эталонами
    if (!update) {
        await copyExpectedToActual();
    }

    void runChromium();
    await waitUntilUsed(CHROMIUM_PORT, PORT_RETRY_MS, PORT_TIMEOUT_MS);

    // Запускаем тесты; не падаем, т.к. нужно сделать отчет
    try {
        await runTest({update, pathList, env, timeout});
    } catch (e) {
        testError = e;
    } finally {
        await stopChromium();
    }

    // Переносим актуальные скриншоты в одну папку, откуда их подберет reg-suit
    await screenshotWalk(TEMP_SCREENS_DIR, {isActual: true});

    // Сравниваем скриншоты и делаем отчет
    await compareScreenshots();

    // Чистим временные файлы
    await clearTempFiles();

    if (testError) {
        throw testError;
    }
}

async function runChromium() {
    return execa('docker-compose', ['-f', serviceResolve('docker-compose.yaml'), 'up', 'chromium'], {
        stderr: 'inherit'
    });
}

async function stopChromium() {
    return execa('docker-compose', ['-f', serviceResolve('docker-compose.yaml'), 'stop', 'chromium'], {
        stdout: 'inherit',
        stderr: 'inherit'
    });
}

async function runTest({env, update, pathList = [], timeout, retry}: Partial<HandleInput>) {
    const args = ['--config', serviceResolve('./tools/jest/config.puppeteer.js')];

    if (update) {
        args.push('--updateSnapshot');
    }

    args.push(...pathList);

    const domain = getDomain(env);

    writeInfo(`Running tests on ${domain}`);

    return await execa('npx', [config.cli.jestBinary, ...args], {
        stdout: 'inherit',
        stderr: 'inherit',
        env: {
            ...(update ? {UPDATE_SCREEN: '1'} : {}),
            NODE_ENV: 'testing',
            TEST_DOMAIN: domain,
            TEST_TIMEOUT: timeout,
            TEST_RETRY: retry,
            CHROMIUM_PORT: `${CHROMIUM_PORT}`
        }
    });
}

function getDomain(env: string = 'testing'): string {
    // TODO check domain
    switch (env) {
        case 'testing':
            return TESTING_DOMAIN;
        case 'dev':
            return DEV_DOMAIN;
        default:
            return env;
    }
}

async function compareScreenshots() {
    await execa('npx', [config.cli.regSuitBinary, 'compare'], {
        stdout: 'inherit',
        stderr: 'inherit'
    });
}

async function clearTempFiles() {
    // Удаляем папку для временных скриншотов
    await fs.rmdir(TEMP_SCREENS_DIR, {recursive: true});
    // Во время прогона тестов здесь появляются диффы, удаляем их из-за ненадобности
    await fs.rmdir(serviceResolve('./src/tests/__diff__'), {recursive: true});
}

function writeInfo(msg: string) {
    // eslint-disable-next-line no-console
    return console.log(kleur.cyan().bold(msg));
}

const SCREENS_FORMATS = ['png'];

async function copyScreenshots(paths: string[], destination: string) {
    for (const path of paths) {
        const screenName = path.split('/').pop();

        await fs.copyFile(path, `${destination}/${screenName}`);
    }
}

interface ScreenshotWalkOptions {
    isActual?: boolean;
}

async function screenshotWalk(destination: string, options: ScreenshotWalkOptions = {}) {
    const {isActual} = options;
    const screenshotDir = isActual ? 'actual' : 'expected';

    try {
        await fs.access(destination);
    } catch (e) {
        await fs.mkdir(destination, {recursive: true});
    }

    const screenshots = await glob([
        serviceResolve(`./src/tests/**/${screenshotDir}/*.(${SCREENS_FORMATS.join('|')})`)
    ]);

    await copyScreenshots(screenshots, destination);
}

async function copyExpectedToActual() {
    const paths = await glob([serviceResolve(`./src/tests/**/expected/*.(${SCREENS_FORMATS.join('|')})`)]);

    for (const path of paths) {
        // Беру с префиксом screenshots, чтобы не было совпадений с названием теста
        const destination = path.replace('screenshots/expected', 'screenshots/actual');
        const destinationDir = destination.split('/').slice(0, -1).join('/');

        try {
            await fs.access(destinationDir);
        } catch (e) {
            await fs.mkdir(destinationDir, {recursive: true});
        }

        await fs.copyFile(path, destination);
    }
}
