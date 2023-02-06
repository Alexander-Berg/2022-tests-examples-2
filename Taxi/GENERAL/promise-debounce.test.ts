import {promiseDebounce} from './promise-debounce';

async function delay(time: number): Promise<void> {
    return new Promise((resolve) => {
        setTimeout(resolve, time);
    });
}

function asyncFn(value: number, wait = 100): Promise<number> {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve(value);
        }, wait);
    });
}

describe('/lib/promise-debounce', () => {
    it('should call async function only once', async () => {
        const asyncFnDebounced = promiseDebounce(asyncFn, 300);

        const promise1 = asyncFnDebounced(1);
        await delay(100);
        const promise2 = asyncFnDebounced(2);

        const results = await Promise.all([promise1, promise2]);

        expect(results[0]).toEqual(2);
        expect(results[1]).toEqual(2);
    });
});
