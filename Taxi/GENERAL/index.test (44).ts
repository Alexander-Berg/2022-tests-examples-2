import {createStream, Logger, stringifyTskv, taxiFormatter, Transport} from '@lavka-js-toolbox/logger';
import {ILockProvider} from '@lavka-js-toolbox/mutex';
import path from 'path';

import {CronLauncher} from './cron-launcher';

class TestLockProvider implements ILockProvider {
    public async createLock() {}

    public async releaseLock() {}

    public async isLockExist() {
        return false;
    }
}

const CRON = '0 0 1 1 *'; // Каждый год, чтобы не запустился лишний раз в тестах

describe('package "cron-launcher"', () => {
    jest.setTimeout(5_000);

    let logger: Logger;
    let logs: string[] = [];

    beforeEach(() => {
        jest.clearAllMocks();
        jest.resetAllMocks();

        const {transport, logs: logArr} = createArrayTransport();
        logs = logArr;

        logger = new Logger({
            name: 'test_logger',
            commonMeta: {version: 'unknown', env: 'unknown'},
            stream: createStream({level: 'info', transport})
        });
    });

    it('should finish cron', async () => {
        const lockProvider = new TestLockProvider();
        const cronLauncher = new CronLauncher({
            key: 'test',
            cron: CRON,
            lockProvider,
            lockTimeoutMs: 2_000,
            workerPath: path.resolve('./dist/src/test/success.js'),
            runOnInit: true,
            logger
        });

        await new Promise((resolve) => setTimeout(resolve, 2_000));

        cronLauncher.stop();

        expect(logs).toHaveLength(1);
        expect(logs[0].includes('scheduler "scheduler-test" complete')).toBe(true);
    });

    it('should throw error if lock did not acquired', async () => {
        jest.spyOn(TestLockProvider.prototype, 'isLockExist').mockImplementation(async () => {
            return true;
        });

        const lockProvider = new TestLockProvider();
        const cronLauncher = new CronLauncher({
            key: 'test',
            cron: CRON,
            lockProvider,
            lockTimeoutMs: 2_000,
            workerPath: path.resolve('./dist/src/test/success.js'),
            runOnInit: true,
            waitAcquireTimeoutMs: 1_000,
            logger
        });

        await new Promise((resolve) => setTimeout(resolve, 2_000));

        cronLauncher.stop();

        expect(logs).toHaveLength(2);
        expect(logs[0].includes('scheduler "scheduler-test" failed')).toBe(true);
        expect(logs[1].includes('Locke mutex wait acquire timeout')).toBe(true);
    });

    it('should throw error if worker return known error', async () => {
        const lockProvider = new TestLockProvider();
        const cronLauncher = new CronLauncher({
            key: 'test',
            cron: CRON,
            lockProvider,
            lockTimeoutMs: 2_000,
            workerPath: path.resolve('./dist/src/test/known-error.js'),
            runOnInit: true,
            waitAcquireTimeoutMs: 1_000,
            logger
        });

        await new Promise((resolve) => setTimeout(resolve, 2_000));

        cronLauncher.stop();

        expect(logs).toHaveLength(2);
        expect(logs[0].includes('scheduler "scheduler-test" failed')).toBe(true);
        expect(logs[1].includes('some known error :)')).toBe(true);
    });

    it('should throw error if worker returns unknown error', async () => {
        const lockProvider = new TestLockProvider();
        const workerPath = path.resolve('./dist/src/test/unknown-error.js');

        const cronLauncher = new CronLauncher({
            key: 'test',
            cron: CRON,
            lockProvider,
            lockTimeoutMs: 2_000,
            workerPath,
            runOnInit: true,
            waitAcquireTimeoutMs: 1_000,
            logger
        });

        await new Promise((resolve) => setTimeout(resolve, 2_000));

        cronLauncher.stop();

        expect(logs).toHaveLength(2);
        expect(logs[0].includes('scheduler "scheduler-test" failed')).toBe(true);
        expect(logs[1].includes(`Worker ${workerPath} unexpectedly exited with code 0`)).toBe(true);
    });

    it('should successfully finish task if worker finished with zero code and acceptZeroExitCode: true', async () => {
        const lockProvider = new TestLockProvider();
        const cronLauncher = new CronLauncher({
            key: 'test',
            cron: CRON,
            lockProvider,
            lockTimeoutMs: 2_000,
            workerPath: path.resolve('./dist/src/test/zero-exit-code.js'),
            runOnInit: true,
            acceptZeroExitCode: true,
            logger
        });

        await new Promise((resolve) => setTimeout(resolve, 2_000));

        cronLauncher.stop();

        expect(logs).toHaveLength(1);
        expect(logs[0].includes('scheduler "scheduler-test" complete')).toBe(true);
    });

    it('should throw if worker finished with non-zero code and acceptZeroExitCode: true', async () => {
        const lockProvider = new TestLockProvider();
        const workerPath = path.resolve('./dist/src/test/non-zero-exit-code.js');

        const cronLauncher = new CronLauncher({
            key: 'test',
            cron: CRON,
            lockProvider,
            lockTimeoutMs: 2_000,
            workerPath,
            runOnInit: true,
            acceptZeroExitCode: true,
            logger
        });

        await new Promise((resolve) => setTimeout(resolve, 2_000));

        cronLauncher.stop();

        expect(logs).toHaveLength(2);
        expect(logs[0].includes('scheduler "scheduler-test" failed')).toBe(true);
        expect(logs[1].includes(`Worker ${workerPath} unexpectedly exited with code 1`)).toBe(true);
    });

    it('should throw error if cron timeout', async () => {
        const lockProvider = new TestLockProvider();
        const cronLauncher = new CronLauncher({
            key: 'test',
            cron: CRON,
            lockProvider,
            lockTimeoutMs: 1_000,
            workerPath: path.resolve('./dist/src/test/too-long.js'),
            runOnInit: true,
            waitAcquireTimeoutMs: 1_000,
            logger
        });

        await new Promise((resolve) => setTimeout(resolve, 2_000));

        cronLauncher.stop();

        expect(logs).toHaveLength(2);
        expect(logs[0].includes('scheduler "scheduler-test" failed')).toBe(true);
        expect(logs[1].includes('cron timeout: 1000 ms')).toBe(true);
    });
});

function createArrayTransport({logs = []}: {logs?: string[]} = {}) {
    const writer = (message: string) => logs.push(message);
    const formatTaxi = taxiFormatter();
    const transport: Transport = (report) => writer(stringifyTskv(formatTaxi(report)));

    return {logs, transport, writer};
}
