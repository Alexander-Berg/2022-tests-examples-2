beforeEach(function() {
    jest.resetModules();
});

test('run', async function() {
    jest.setMock('../../../utils/s3-aws', {
        bucket: 'abc',
        walk: func => {
            const lastWrite = '2020-05-06T13:16:55.832Z';
            func({ Key: 'a.js', LastModified: lastWrite });
            func({ Key: 'a.js.br', LastModified: lastWrite });
            func({ Key: 'a.js.gz', LastModified: lastWrite });
            func({ Key: 'b.js', LastModified: lastWrite });
            func({ Key: 'b.js.br', LastModified: lastWrite });
            func({ Key: 'c.css', LastModified: lastWrite });
        },
    });
    jest.setMock('../../../utils/fetchUsedFiles', {
        fetchUsedFiles: () => Promise.resolve(['/a.js', '/b.js', '/c.css']),
    });

    const missing = await require('../run').run();
    expect(missing).toStrictEqual(new Set(['/b.js', '/c.css']));
});

test('run with missing files', async function() {
    jest.setMock('../../../utils/s3-aws', {
        bucket: 'abc',
        walk: func => {
            const lastWrite = new Date();
            func({ isDir: false, path: '/a.js', lastWrite, size: 0 });
            func({ isDir: false, path: '/a.js.br', lastWrite, size: 0 });
            func({ isDir: false, path: '/a.js.gz', lastWrite, size: 0 });
            func({ isDir: false, path: '/b.js.br', lastWrite, size: 0 });
            func({ isDir: false, path: '/c.css', lastWrite, size: 0 });
        },
    });
    jest.setMock('../../../utils/fetchUsedFiles', {
        fetchUsedFiles: () => Promise.resolve(['/a.js', '/b.js', '/c.css']),
    });

    await expect(require('../run').run()).rejects.toThrow('All used files should be found');
});
