const dateMock = require('jest-date-mock');

beforeEach(function() {
    jest.resetModules();

    jest.mock('../utils/s3-aws', () => {
        return { bucket: 'abc' };
    });
});

describe('dateRange', function() {
    beforeEach(function() {
        dateMock.clear();
    });

    test('2020-01-01', function() {
        dateMock.advanceTo('2020-01-01');
        const { usedDateRange } = require('../utils/fetchUsedFiles');
        expect(usedDateRange()).toStrictEqual(['2019-11-30', '2019-12-31']);
    });

    test('2020-01-02', function() {
        dateMock.advanceTo('2020-01-02');
        const { usedDateRange } = require('../utils/fetchUsedFiles');
        expect(usedDateRange()).toStrictEqual(['2019-12-01', '2020-01-01']);
    });

    test('2020-03-02', function() {
        dateMock.advanceTo('2020-03-02');
        const { usedDateRange } = require('../utils/fetchUsedFiles');
        expect(usedDateRange()).toStrictEqual(['2020-02-01', '2020-03-01']);
    });

    test('2020-03-31', function() {
        dateMock.advanceTo('2020-03-31');
        const { usedDateRange } = require('../utils/fetchUsedFiles');
        expect(usedDateRange()).toStrictEqual(['2020-03-01', '2020-03-30']);
    });
});

test('fetchUsedFiles', async function() {
    jest.mock('../utils/yql', () => {
        return { yql: () => Promise.resolve([
            ['/s3/abc/some.js'],
            ['/s3/abc///some.js'],
            ['/s3/abc/some/other.js'],
            ['/s3/abc/some/'],
        ]) };
    });
    const { fetchUsedFiles } = require('../utils/fetchUsedFiles');
    expect(await fetchUsedFiles(1)).toStrictEqual(['/some.js', '/some/other.js']);
});

test('fetchUsedFiles to throw', async function() {
    jest.mock('../utils/yql', () => {
        return { yql: () => Promise.resolve([
            ['/s3/other-bucket/some.js'],
        ]) };
    });
    const { fetchUsedFiles } = require('../utils/fetchUsedFiles');
    await expect(fetchUsedFiles()).rejects.toThrow('Got strange request from yql: "/s3/other-bucket/some.js"');
});
