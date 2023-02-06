import { withRetry } from '@server-libs/node-tools/with-retry';
import * as utils from '@server-libs/node-tools/utils';

jest.mock('@server-libs/node-tools/utils', () => ({
    sleep: jest.fn(),
}));

function successOperation(attempt: number): Promise<number> {
    return new Promise((res, rej) => {
        res(attempt);
    });
}

function failedOperation(attempt: number): Promise<number> {
    return new Promise((res, rej) => {
        rej(attempt);
    });
}

function shouldRetry(res: number | Error): boolean {
    return res < 3;
}

describe('with retry', () => {
    it('should retry operation 5 times', async () => {
        const res = await withRetry(successOperation, 5, () => true, 100);
        expect(res).toBe(5);
    });

    it('should retry before shouldRetry returns true', async () => {
        const res = await withRetry(successOperation, 5, shouldRetry, 0);
        expect(res).toBe(3);
    });

    it('should throw error if operation failed and attempts are over', async () => {
        try {
            await withRetry(failedOperation, 5, () => true, 0);
        } catch (err) {
            expect(err).toBe(5);
        }
    });

    it('should linear increase delay if withBackoffRetry flag passed', async () => {
        const delay = 5;
        await withRetry(successOperation, 4, () => true, delay, true);
        expect(utils.sleep).toHaveBeenCalledWith(delay);
        expect(utils.sleep).toHaveBeenCalledWith(2 * delay);
        expect(utils.sleep).toHaveBeenCalledWith(3 * delay);
    });
});
