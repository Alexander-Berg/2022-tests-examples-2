import {createStream, Logger} from '@lavka-js-toolbox/logger';
import nock from 'nock';

import {YT_ARNOLD_HOST, YtProvider} from './index';

const YT_HOST = 'some.yt.host';

describe('package "yt-provider" - YtProvider()', () => {
    const noopTransport = () => {};

    let provider: YtProvider;
    let logger: Logger;

    beforeAll(async () => {
        nock.disableNetConnect();
        nock.enableNetConnect(/localhost/);
    });

    afterAll(async () => {
        nock.enableNetConnect();
    });

    afterEach(async () => {
        nock.cleanAll();
    });

    beforeEach(async () => {
        nock(YT_ARNOLD_HOST).get('/hosts').reply(200, [YT_HOST]);

        logger = new Logger({
            name: 'test_logger',
            commonMeta: {version: 'unknown', env: 'unknown'},
            stream: createStream({level: 'info', transport: noopTransport})
        });

        provider = new YtProvider({
            logger,
            token: 'token',
            cluster: 'arnold'
        });
    });

    it('should read table with params', async () => {
        nock(`http://${YT_HOST}`)
            .get('/api/v3/read_table')
            .query({
                path: '//home/dir/some_key{col1,col2}[#2:#8]'
            })
            .reply(() => [200, '\n\n{"foo":"value1","bar":1}\n\n{"foo":"value2","bar":2}\n']);

        const rows = await provider.readTable({
            path: '//home/dir/some_key',
            filterColumns: ['col1', 'col2'],
            pagination: {
                offset: 2,
                limit: 6
            }
        });

        expect(nock.pendingMocks()).toHaveLength(0);
        expect(rows).toEqual([
            {
                foo: 'value1',
                bar: 1
            },
            {
                foo: 'value2',
                bar: 2
            }
        ]);
    });

    it('should read table without pagination', async () => {
        nock(`http://${YT_HOST}`)
            .get('/api/v3/read_table')
            .query({
                path: '//home/dir/some_key{col1,col2}'
            })
            .reply(() => [200, '\n\n{"foo":"value1","bar":1}\n\n{"foo":"value2","bar":2}\n']);

        const rows = await provider.readTable({
            path: '//home/dir/some_key',
            filterColumns: ['col1', 'col2']
        });

        expect(nock.pendingMocks()).toHaveLength(0);
        expect(rows).toEqual([
            {
                foo: 'value1',
                bar: 1
            },
            {
                foo: 'value2',
                bar: 2
            }
        ]);
    });

    it('should check is table exist', async () => {
        nock(`http://${YT_HOST}`)
            .get('/api/v3/exists')
            .query({
                path: '//home/dir/some_key'
            })
            .reply(200, false as never);

        const isExist = await provider.exist('//home/dir/some_key');
        expect(isExist).toBe(false);
        expect(nock.pendingMocks()).toHaveLength(0);
    });

    it('should return table rows count', async () => {
        nock(`http://${YT_HOST}`)
            .get('/api/v3/get')
            .query({
                path: '//home/dir/some_key/@'
            })
            .reply(200, {
                row_count: 123
            });

        const count = await provider.getRowsCount('//home/dir/some_key');
        expect(count).toBe(123);
        expect(nock.pendingMocks()).toHaveLength(0);
    });
});
