import {createStream, Logger} from '@lavka-js-toolbox/logger';

import {MutexProvider} from './mutex-provider';
import {ILockProvider} from './types';

class TestLockProvider implements ILockProvider {
    public async createLock() {}

    public async releaseLock() {}

    public async isLockExist() {
        return false;
    }
}

describe('package "mutex"', () => {
    jest.setTimeout(5_000);

    const noopTransport = () => {};
    let logger: Logger;

    beforeEach(() => {
        jest.clearAllMocks();

        logger = new Logger({
            name: 'test_logger',
            commonMeta: {version: 'unknown', env: 'unknown'},
            stream: createStream({level: 'info', transport: noopTransport})
        });
    });

    it('should check lock by specified interval', async () => {
        let isLockExistCount = 0;

        jest.spyOn(TestLockProvider.prototype, 'isLockExist').mockImplementation(async () => {
            isLockExistCount++;
            return true;
        });

        const lockProvider = new TestLockProvider();
        const mutexProvider = new MutexProvider({
            lockProvider,
            checkAcquireIntervalMs: 500,
            waitAcquireTimeoutMs: 2_000,
            logger
        });

        try {
            await mutexProvider.acquireLock();
        } catch {} // eslint-disable-line no-empty

        expect(isLockExistCount).toBeGreaterThanOrEqual(3);
        expect(isLockExistCount).toBeLessThanOrEqual(4);
    });

    it('should throw error if acquire timeout', async () => {
        const lockProvider = new TestLockProvider();
        const mutexProvider = new MutexProvider({
            lockProvider,
            checkAcquireIntervalMs: 500,
            waitAcquireTimeoutMs: 1_000,
            logger
        });

        jest.spyOn(TestLockProvider.prototype, 'isLockExist').mockImplementation(async () => {
            return true;
        });

        await expect(mutexProvider.acquireLock()).rejects.toThrow(
            '[MutexProvider::acquireLock()] Locke mutex wait acquire timeout'
        );
    });

    it('should return function to release lock', async () => {
        const lockProvider = new TestLockProvider();
        const mutexProvider = new MutexProvider({
            lockProvider,
            checkAcquireIntervalMs: 500,
            waitAcquireTimeoutMs: 1_000,
            logger
        });

        let isLockReleased = false;
        let isLockCreated = false;

        jest.spyOn(TestLockProvider.prototype, 'isLockExist').mockImplementation(async () => {
            return false;
        });

        jest.spyOn(TestLockProvider.prototype, 'releaseLock').mockImplementation(async () => {
            isLockReleased = true;
        });

        jest.spyOn(TestLockProvider.prototype, 'createLock').mockImplementation(async () => {
            isLockCreated = true;
        });

        const {release} = await mutexProvider.acquireLock();
        await release();

        expect(isLockReleased).toBe(true);
        expect(isLockCreated).toBe(true);
    });
});
