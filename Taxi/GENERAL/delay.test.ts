import {delay} from './delay';

const MILLISECONDS = 1_000_000;

describe('function delay', () => {
    it('should resolve in a half of the second', async () => {
        const promise = delay(0.5);
        const start = process.hrtime();

        await promise;

        const [sec, mls] = process.hrtime(start);

        expect(sec).toBe(0);
        expect(mls).toBeGreaterThanOrEqual(500 * MILLISECONDS);
        expect(mls).toBeLessThan(600 * MILLISECONDS);
    });
});
