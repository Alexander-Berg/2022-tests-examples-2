import LocalStorage from '../localStorage';

const timeout = async delay => new Promise(resolve => setTimeout(resolve, delay));

describe('LocalStorage', function () {
    const NAMESPACE_1 = 'TEST_NAMESPACE_1';
    const NAMESPACE_2 = 'TEST_NAMESPACE_2';
    const KEY_1 = 'KEY_1';
    const KEY_2 = 'KEY_2';
    const VALUE = 'VALUE';
    const instance = LocalStorage.createInstance({namespace: NAMESPACE_1});
    const instanceAnother = LocalStorage.createInstance({namespace: NAMESPACE_2});

    beforeEach(() => {
        instance.clear();
    });

    test('isAvalable', () => {
        expect(LocalStorage.isAvailable()).toBe(true);
        expect(LocalStorage.isAvailable({localStorageImpl: null})).toBe(false);
        expect(LocalStorage.isAvailable({localStorageImpl: {}})).toBe(false);
    });

    test('createInstance', () => {
        expect(LocalStorage.createInstance({namespace: NAMESPACE_1}) === instance).toBe(true);
        expect(LocalStorage.createInstance({namespace: NAMESPACE_2}) === instanceAnother).toBe(true);
        expect(LocalStorage.createInstance() === LocalStorage.createInstance()).toBe(true); //eslint-disable-line no-self-compare
    });

    test('constructor and createInstance throws when namespace is not string', () => {
        expect(() => new LocalStorage({namespace: 1})).toThrow();
    });

    test('set, get, delete, has, clear', () => {
        instance.set(KEY_1, VALUE);
        instance.set(KEY_2, VALUE);

        expect(instance.has(KEY_1)).toBe(true);
        expect(instance.get(KEY_1)).toBe(VALUE);
        expect(instance.has(KEY_2)).toBe(true);
        expect(instance.get(KEY_2)).toBe(VALUE);

        instance.delete(KEY_2);

        expect(instance.has(KEY_1)).toBe(true);
        expect(instance.get(KEY_1)).toBe(VALUE);
        expect(instance.has(KEY_2)).toBe(false);
        expect(instance.get(KEY_2)).toBe(undefined);

        instance.clear();

        expect(instance.has(KEY_1)).toBe(false);
        expect(instance.get(KEY_1)).toBe(undefined);
    });

    test('clear own namespace, empty namespace clears whole', () => {
        instance.set(KEY_1, VALUE);
        instanceAnother.set(KEY_2, VALUE);

        expect(instance.has(KEY_1)).toBe(true);
        expect(instance.get(KEY_1)).toBe(VALUE);
        expect(instanceAnother.has(KEY_2)).toBe(true);
        expect(instanceAnother.get(KEY_2)).toBe(VALUE);

        instance.clear();

        expect(instance.has(KEY_1)).toBe(false);
        expect(instance.get(KEY_1)).toBe(undefined);
        expect(instanceAnother.has(KEY_2)).toBe(true);
        expect(instanceAnother.get(KEY_2)).toBe(VALUE);

        LocalStorage.createInstance().clear();

        expect(instance.has(KEY_1)).toBe(false);
        expect(instance.get(KEY_1)).toBe(undefined);
        expect(instanceAnother.has(KEY_2)).toBe(false);
        expect(instanceAnother.get(KEY_2)).toBe(undefined);
    });

    test('ignore and delete expired', async () => {
        const KEY_TEMPORAL = 'KEY_TEMPORAL';
        const KEY_PERMANENT = 'KEY_PERMANENT';
        const DELAY = 5;

        instance.set(KEY_TEMPORAL, VALUE, {expire: DELAY});
        instance.set(KEY_PERMANENT, VALUE);

        expect(instance.has(KEY_TEMPORAL)).toBe(true);
        expect(instance.has(KEY_PERMANENT)).toBe(true);

        expect(instance.get(KEY_TEMPORAL)).toBe(VALUE);
        expect(instance.get(KEY_PERMANENT)).toBe(VALUE);

        await timeout(DELAY * 2);

        expect(instance.get(KEY_TEMPORAL)).toBe(undefined);
        expect(instance.get(KEY_PERMANENT)).toBe(VALUE);

        expect(instance.has(KEY_TEMPORAL)).toBe(false);
        expect(instance.has(KEY_PERMANENT)).toBe(true);
    });
});
