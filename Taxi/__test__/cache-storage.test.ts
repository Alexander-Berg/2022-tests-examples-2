import {getCache, setCache} from '../cache-storage';

test('cache-storage', async () => {
    const seconds = 1;
    const value = 1;

    setCache(value, {
        lifetime: seconds,
        makeKey: () => 'key'
    });

    const res1 = getCache('key');
    const res2 = getCache('key');

    await new Promise(resolve => setTimeout(resolve, seconds * 1000 * 2));

    const res3 = getCache('key');

    expect(res1).toBe(value);
    expect(res2).toBe(value);
    expect(res3).toBe(undefined);
});
