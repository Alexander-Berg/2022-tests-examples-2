import {retry} from '../utils';

const RETRIES = 2;

describe('retry', () => {
    test('retry - success case', async () => {
        const mockFn = jest.fn((n: number) => {
            return 1;
        });

        const func = retry(mockFn, RETRIES);

        const result = await func(1);
        expect(result).toBe(1);
        expect(mockFn).toHaveBeenCalledWith(1);
        expect(mockFn).toHaveBeenCalledTimes(1);
    });

    test('retry - error case', async () => {
        const mockFn = jest.fn((n: number) => {
            throw new Error();
        });

        const func = retry(mockFn, RETRIES);

        try {
            await func(1);
        } catch (e) {
            expect(mockFn).toHaveBeenCalledWith(1);
            expect(mockFn).toHaveBeenCalledTimes(RETRIES + 1);
            return;
        }

        throw new Error('Exception was not thrown');
    });

    test('retry - invokes at least once by default', async () => {
        const mockFn = jest.fn((n: number) => {
            return 1;
        });

        const func = retry(mockFn);

        const result = await func(1);
        expect(result).toBe(1);
        expect(mockFn).toHaveBeenCalledWith(1);
        expect(mockFn).toHaveBeenCalledTimes(1);
    });
});
