beforeEach(function() {
    jest.resetModules();
});

test('missing bucket', function() {
    expect(() => {
        process.env.S3_BUCKET = '';
        require('../utils/s3');
    }).toThrow();
});

test('bucket', function() {
    process.env.S3_BUCKET = 'abc';
    expect(require('../utils/s3').bucket).toBe('abc');
});

test('ls', async function() {
    process.env.S3_BUCKET = 'abc';
    jest.mock('../utils/call', () => {
        return { call: jest.fn(() => Promise.resolve('')) };
    });
    let s3 = require('../utils/s3');
    let { call } = require('../utils/call');
    call.mockImplementation(() => Promise.resolve(`
2018-10-11 13:08:14        189 bell_dummy_unread_none_skin_36.png
                           PRE tune/
`));
    expect(await s3.ls('/')).toEqual([{
        isDir: false,
        lastWrite: new Date(2018, 9, 11, 13, 8, 14),
        path: 'bell_dummy_unread_none_skin_36.png',
        size: 189,
    }, {
        isDir: true,
        lastWrite: null,
        path: 'tune/',
        size: 0,
    }]);
    expect(call).toHaveBeenNthCalledWith(1, 'aws --endpoint-url=http://s3.mds.yandex.net s3 ls s3://abc/');
    call.mockImplementation(() => Promise.resolve(`
2018-10-11 13:08:14        189 bell_dummy_unread_none_skin_36.png
2018-04-11 13:08:14       1234 tune/something.js
`));
    expect(await s3.ls('/', { recursive: true })).toEqual([{
        isDir: false,
        lastWrite: new Date(2018, 9, 11, 13, 8, 14),
        path: 'bell_dummy_unread_none_skin_36.png',
        size: 189,
    }, {
        isDir: false,
        lastWrite: new Date(2018, 3, 11, 13, 8, 14),
        path: 'tune/something.js',
        size: 1234,
    }]);
    expect(call).toHaveBeenNthCalledWith(2, 'aws --endpoint-url=http://s3.mds.yandex.net s3 ls s3://abc/ --recursive');
    call.mockImplementation(() => Promise.resolve(''));
    expect(await s3.ls('/dir', { recursive: true })).toEqual([]);
    expect(call).toHaveBeenNthCalledWith(3, 'aws --endpoint-url=http://s3.mds.yandex.net s3 ls s3://abc/dir --recursive');
});

test('walk', async function() {
    process.env.S3_BUCKET = 'abc';

    jest.mock('../utils/call', () => {
        let callImpl = str => {
            return Promise.resolve({
                'aws --endpoint-url=http://s3.mds.yandex.net s3 ls s3://abc/': `
2018-10-11 13:08:14        189 some.js
                           PRE dir/
`,
                'aws --endpoint-url=http://s3.mds.yandex.net s3 ls s3://abc/dir/': `
2018-10-11 13:08:14        189 other.css
                           PRE other2/
                           PRE other3/
`,
                'aws --endpoint-url=http://s3.mds.yandex.net s3 ls s3://abc/dir/other2/ --recursive': '',
                'aws --endpoint-url=http://s3.mds.yandex.net s3 ls s3://abc/dir/other3/ --recursive': `
                           PRE dir/other3/other4/
`,
                'aws --endpoint-url=http://s3.mds.yandex.net s3 ls s3://abc/dir/other3/other4/ --recursive': `
2018-10-11 13:08:14        189 dir/other3/other4/data.txt
                `,
            }[str]);
        };

        return { call: jest.fn(callImpl) };
    });
    let s3 = require('../utils/s3');
    let iter = jest.fn();
    await s3.walk(iter);
    expect(iter).toHaveBeenNthCalledWith(1, {
        isDir: false,
        lastWrite: new Date(2018, 9, 11, 13, 8, 14),
        path: '/some.js',
        size: 189,
    });
    expect(iter).toHaveBeenNthCalledWith(2, {
        isDir: false,
        lastWrite: new Date(2018, 9, 11, 13, 8, 14),
        path: '/dir/other.css',
        size: 189,
    });
    expect(iter).toHaveBeenNthCalledWith(3, {
        isDir: false,
        lastWrite: new Date(2018, 9, 11, 13, 8, 14),
        path: '/dir/other3/other4/data.txt',
        size: 189,
    });
});
