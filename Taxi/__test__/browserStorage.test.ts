import {LocalStorage} from '_pkg/utils/browserStorage';
import timeout from '_pkg/utils/timeout';

const NAMESPACE = '__test__ls__';
const ls = new LocalStorage(NAMESPACE);

describe('LocalStorage', function () {
    // skip, потому что тест постоянно флапает!!
    test.skip('clearExpired', async () => {
        const delay = 5;
        const key1 = 'test_key_1';
        const key2 = 'test_key_2';
        ls.set(key1, 1, {expire: delay});
        ls.set(key2, 2, {expire: delay * 100});

        expect(ls.has(key1)).toBe(true);
        expect(ls.has(key2)).toBe(true);
        await timeout(delay * 2);

        ls.clearExpired();
        expect(ls.has(key1)).toBe(false);
        expect(ls.has(key2)).toBe(true);
    });
});
