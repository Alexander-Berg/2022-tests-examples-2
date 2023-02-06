beforeEach(function() {
    jest.resetModules();
    jest.setMock('../../../utils/s3-aws', {
        bucket: 'abc',
    });
    jest.setMock('../../../utils/publishResource', {
        addTaskLog: () => Promise.resolve(),
    });
    jest.setMock('fs', {
        promises: {
            writeFile: () => Promise.resolve(),
        },
    });
});

test('shouldRemoveFile', function() {
    const { shouldRemoveFile } = require('../run');

    expect(shouldRemoveFile('/test.js', new Date())).toBe(false);
    expect(shouldRemoveFile('/test.js', new Date(1997))).toBe(true);
});

describe('run', function() {
    const makeTest = (s3Files, usedFiles, expectedFilesToRemove) => {
        return async() => {
            jest.setMock('../../../utils/s3-aws', {
                bucket: 'abc',
                walk: func => {
                    const oldWrite = '1997-05-06T13:16:55.832Z';
                    const newWrite = '2020-05-06T13:16:55.832Z';

                    for (const file of s3Files) {
                        func({ Key: file.Key, LastModified: file.old ? oldWrite : newWrite });
                    }
                },
            });
            jest.setMock('../../../utils/fetchUsedFiles', {
                fetchUsedFiles: () => Promise.resolve(usedFiles),
            });

            const actualFilesToRemove = await require('../run').run();
            expect(actualFilesToRemove).toStrictEqual(new Set(expectedFilesToRemove));
        };
    };

    test('old, used', makeTest([
        { Key: 'a.js', old: true },
        { Key: 'a.js.br', old: true },
        { Key: 'a.js.gz', old: true },
    ], [
        '/a.js',
    ], []));

    test('old, not used', makeTest([
        { Key: 'a.js', old: true },
        { Key: 'a.js.br', old: true },
        { Key: 'a.js.gz', old: true },
    ], [
    ], [
        '/a.js',
        '/a.js.br',
        '/a.js.gz',
    ]));

    test('new, not used', makeTest([
        { Key: 'a.js' },
        { Key: 'a.js.br' },
        { Key: 'a.js.gz' },
    ], [
    ], [
    ]));

    test('new, used', makeTest([
        { Key: 'a.js' },
        { Key: 'a.js.br' },
        { Key: 'a.js.gz' },
    ], [
        '/a.js',
    ], [
    ]));

    test('mixed dates, not used', makeTest([
        { Key: 'a.js', old: true },
        { Key: 'a.js.br', old: true },
        { Key: 'a.js.gz' },
    ], [
    ], [
    ]));

    test('old, used minified files', makeTest([
        { Key: 'a.js', old: true },
        { Key: 'a.js.br', old: true },
        { Key: 'a.js.gz', old: true },
    ], [
        '/a.js.br',
    ], [
    ]));

    test('old, no minified files, not used', makeTest([
        { Key: 'a.js', old: true },
    ], [
    ], [
        '/a.js',
    ]));

    test('old, no minified files, used', makeTest([
        { Key: 'a.js', old: true },
    ], [
        '/a.js',
    ], [
    ]));
});

test('run with missing files', async function() {
    jest.setMock('../../../utils/s3-aws', {
        bucket: 'abc',
        walk: func => {
            const oldWrite = new Date(1997);
            func({ isDir: false, path: '/a.js', lastWrite: oldWrite, size: 0 });
            func({ isDir: false, path: '/a.js.br', lastWrite: oldWrite, size: 0 });
            func({ isDir: false, path: '/a.js.gz', lastWrite: oldWrite, size: 0 });
            func({ isDir: false, path: '/b.js', lastWrite: oldWrite, size: 0 });
            func({ isDir: false, path: '/b.js.br', lastWrite: oldWrite, size: 0 });
        },
    });
    jest.setMock('../../../utils/fetchUsedFiles', {
        fetchUsedFiles: () => Promise.resolve(['/a.js', '/c.css']),
    });

    await expect(require('../run').run()).rejects.toThrow('All used files should be found');
});
