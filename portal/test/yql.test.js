beforeEach(function() {
    jest.resetModules();
});

test('yql', async function() {
    process.env.S3_BUCKET = 'abc';

    const writeFile = jest.fn(() => Promise.resolve());
    const readFile = jest.fn(() => Promise.resolve('[["column0 (Int32)"], ["a"], ["b"], ["c"]]'));

    jest.setMock('fs', {
        promises: {
            readFile,
            writeFile,
        },
    });

    const call = jest.fn(() => Promise.resolve(''));
    jest.setMock('../utils/call', {
        call,
    });

    const { yql } = require('../utils/yql');

    expect(await yql('abcde')).toStrictEqual([['a'], ['b'], ['c']]);

    expect(call).toBeCalledWith('./yql --syntax-version 1 -i yql.in.txt -o yql.out.txt -r -f json');

    expect(writeFile).toBeCalledWith('yql.in.txt', 'abcde', { encoding: 'utf-8' });
    expect(readFile).toBeCalledWith('yql.out.txt', 'utf-8');
});
