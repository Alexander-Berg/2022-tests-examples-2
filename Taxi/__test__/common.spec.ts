import {
    findResult,
    fixVariableName,
    getFolder,
    isChildFolder,
    isFilePath,
    isParentFolder,
    isSiblingFolder,
    isValidVariableName,
    makeRelativePath,
    proxyPaths,
    resolveImport,
    uniq,
} from '../common';

describe('utils/common', () => {
    test('isFilePath', () => {
        expect(isFilePath('/a/b/file.ext')).toBe(true);
        expect(isFilePath('/a/b/')).toBe(false);
        expect(isFilePath('/a/b')).toBe(false);
    });

    test('getFolder', () => {
        expect(getFolder('/a/b/file.ext')).toBe('/a/b');
        expect(getFolder('/a/b/')).toBe('/a/b/');
        expect(getFolder('/a/b')).toBe('/a/b');
    });

    test('makeRelativePath', () => {
        expect(makeRelativePath('./a')).toBe('./a');
        expect(makeRelativePath('../a')).toBe('../a');
        expect(makeRelativePath('/a')).toBe('./a');
        expect(makeRelativePath('a')).toBe('./a');
        expect(makeRelativePath('')).toBe('.');
        expect(makeRelativePath('/')).toBe('.');
        expect(makeRelativePath('./')).toBe('.');
    });

    test('resolveImport', () => {
        const path = resolveImport(`${__dirname}/a/file1.yaml`, `${__dirname}/file2.yaml`);

        expect(path).toBe('../file2.yaml');

        const path2 = resolveImport(`${__dirname}/a/file1.yaml`, `${__dirname}/b`);

        expect(path2).toBe('../b');

        const path3 = resolveImport(`${__dirname}/file2.yaml`, `${__dirname}/a/file1.yaml`);

        expect(path3).toBe('./a/file1.yaml');
    });

    test('uniq', () => {
        const arr = [{ x: 1 }, { x: 2 }, { x: 1 }];

        expect(uniq(arr, item => item.x)).toEqual([{ x: 1 }, { x: 2 }]);
    });

    test('isValidVariableName', () => {
        expect(isValidVariableName('_')).toBe(true);
        expect(isValidVariableName('a')).toBe(true);
        expect(isValidVariableName('a_23_d4__')).toBe(true);
        expect(isValidVariableName('$')).toBe(true);

        expect(isValidVariableName('1')).toBe(false);
        expect(isValidVariableName('a-2')).toBe(false);
    });

    test('fixVariableName', () => {
        expect(fixVariableName('12.v3.asdf')).toBe('_12_v3_asdf');
    });

    test('findResult', () => {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const f1 = jest.fn((x?: boolean) => undefined);
        const f2 = jest.fn((x?: boolean) => x);
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const f3 = jest.fn((x?: boolean) => undefined);

        const res = findResult([f1, f2, f3])(false);

        expect(res).toBe(false);
        expect(f1).toHaveBeenCalledTimes(1);
        expect(f2).toHaveBeenCalledTimes(1);
        expect(f3).toHaveBeenCalledTimes(0);
    });

    test('isSiblingFolder', () => {
        expect(isSiblingFolder('a/b/1.yaml', 'a/b/2.yaml')).toBe(true);

        expect(isSiblingFolder('a/b/c/1.yaml', 'a/b/2.yaml')).toBe(false);

        expect(isSiblingFolder('a/b/1.yaml', 'a/b/c/2.yaml')).toBe(false);

        expect(isSiblingFolder('a/b/d/1.yaml', 'a/b/c/2.yaml')).toBe(false);
    });

    test('isChildFolder', () => {
        expect(isChildFolder('a/b/1.yaml', 'a/b/2.yaml')).toBe(false);

        expect(isChildFolder('a/b/c/1.yaml', 'a/b/2.yaml')).toBe(true);

        expect(isChildFolder('a/b/1.yaml', 'a/b/c/2.yaml')).toBe(false);

        expect(isChildFolder('a/b/d/1.yaml', 'a/b/c/2.yaml')).toBe(false);
    });

    test('isParentFolder', () => {
        expect(isParentFolder('a/b/1.yaml', 'a/b/2.yaml')).toBe(false);

        expect(isParentFolder('a/b/c/1.yaml', 'a/b/2.yaml')).toBe(false);

        expect(isParentFolder('a/b/1.yaml', 'a/b/c/2.yaml')).toBe(true);

        expect(isParentFolder('a/b/d/1.yaml', 'a/b/c/2.yaml')).toBe(false);
    });

    test('proxyPaths', () => {
        const proxy = proxyPaths({
            a: {
                b: {
                    c: 1,
                    d: [
                        {
                            e: 2,
                        },
                    ],
                    f: [2],
                },
            },
            g: 2,
        });

        expect(proxy.a.getPath()).toBe('a');
        expect(proxy.a.value.b.getPath()).toBe('a.b');

        expect(proxy.a.value.b.value.c.getPath()).toBe('a.b.c');
        expect(proxy.a.value.b.value.c.value).toBe(1);

        expect(proxy.a.value.b.value.d.getPath()).toBe('a.b.d');
        expect(proxy.a.value.b.value.d.value[0].getPath()).toBe('a.b.d.0');

        expect(proxy.a.value.b.value.d.value[0].value.e.value).toBe(2);
        expect(proxy.a.value.b.value.d.value[0].value.e.getPath()).toBe('a.b.d.0.e');

        expect(proxy.a.value.b.value.f.value[0].value).toBe(2);
        expect(proxy.a.value.b.value.f.value[0].getPath()).toBe('a.b.f.0');

        expect(proxy.g.value).toBe(2);
        expect(proxy.g.getPath()).toBe('g');

        const proxy2 = proxyPaths(2);
        expect(proxy2).toBe(2);

        // non existing key
        expect((proxy.a.value as any).yyy.getPath()).toBe('a.yyy');
        expect((proxy.a.value as any).yyy.value).toBe(undefined);

        expect(Object.keys(proxy)).toEqual(['a', 'g']);

        proxy.g.value = 55;
        expect(proxy.g.value).toBe(55);
    });
});
