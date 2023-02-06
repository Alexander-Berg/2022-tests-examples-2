import {batch} from './utils';

test('batch return result', async () => {
    const fn = jest.fn((x: number) => {
        return Promise.resolve(x);
    });

    const fetch = batch(fn);
    expect(await fetch(1)).toBe(1);
});

test('batch sync', async () => {
    const fn = jest.fn((x: number) => {
        return Promise.resolve(x);
    });

    const fetch = batch(fn);
    await Promise.all(Array.from({length: 10}).map((_, index) => fetch(index % 2)));

    expect(fn).toHaveBeenCalledTimes(2);
    await fetch(0);
    expect(fn).toHaveBeenCalledTimes(3);
});

test('batch async', async () => {
    const delay = 10;
    const fn = jest.fn((x: number) => {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve(x);
            }, delay);
        });
    });

    const fetch = batch(fn);
    await Promise.all(Array.from({length: 10}).map((_, index) => fetch(index % 2)));

    expect(fn).toHaveBeenCalledTimes(2);
    await fetch(0);
    expect(fn).toHaveBeenCalledTimes(3);
});

test('batch clear cache after errors', async () => {
    const delay = 10;
    let counter = 0;
    const fn = jest.fn((x: number) => {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (counter % 2 === 0) {
                    reject(new Error());
                } else {
                    resolve(x);
                }
                counter++;
            }, delay);
        });
    });

    const fetch = batch(fn);
    try {
        await Promise.all(Array.from({length: 9}).map(() => fetch(0)));
        throw new Error('Unexpected code branch');
    } catch {
        expect(fn).toHaveBeenCalledTimes(1);
    }

    await fetch(0);
    expect(fn).toHaveBeenCalledTimes(2);
});
