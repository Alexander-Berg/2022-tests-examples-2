import {seed, uuid} from 'casual';
import {describe, expect, it} from 'tests/jest.globals';

import {MutexWaitAcquireTimeout} from '@/src/errors';
import {Mutex} from 'service/db/mutex';

seed(3);

const TIME_MARGIN = 200;

describe('database mutex', () => {
    it('should lock by key', async () => {
        const key = uuid;
        const waitMs = 500;

        const mutex = new Mutex({key});

        const {releaseLock} = await mutex.acquireLock();
        setTimeout(() => void releaseLock(), waitMs);

        const startTime = new Date().getTime();
        await mutex.acquireLock();
        const time = new Date().getTime() - startTime;

        expect(time >= waitMs && time <= waitMs + TIME_MARGIN).toBeTruthy();
    });

    it('should handle non-released lock', async () => {
        const key = uuid;
        const lockTimeout = 500;

        const mutex = new Mutex({key, lockTimeout});

        await mutex.acquireLock();

        const startTime = new Date().getTime();
        await mutex.acquireLock();
        const time = new Date().getTime() - startTime;

        expect(time >= lockTimeout && time <= lockTimeout + TIME_MARGIN).toBeTruthy();
    });

    it('should handle non-acquired lock', async () => {
        const key = uuid;
        const waitAcquireTimeout = 500;

        const mutex = new Mutex({key, waitAcquireTimeout});

        await mutex.acquireLock();

        const startTime = new Date().getTime();
        await expect(mutex.acquireLock()).rejects.toThrow(MutexWaitAcquireTimeout);

        const time = new Date().getTime() - startTime;
        expect(time).toBeGreaterThanOrEqual(waitAcquireTimeout);
        expect(time).toBeLessThanOrEqual(waitAcquireTimeout + TIME_MARGIN);
    });
});
