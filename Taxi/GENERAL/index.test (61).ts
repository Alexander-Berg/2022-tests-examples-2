import {createStream, Logger, stringifyTskv, taxiFormatter, Transport} from '@lavka-js-toolbox/logger';
import {times} from 'lodash';
import nock from 'nock';

import {YQL_HOST, YqlProvider} from './index';

describe('package "yql-provider" - YqlProvider()', () => {
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

    it('should correct execute query with 2 retry', async () => {
        const id = 'super-id';
        const query = 'select 1';

        const {transport, logs} = createArrayTransport();
        const logger = new Logger({
            name: 'test_logger',
            commonMeta: {version: 'unknown', env: 'unknown'},
            stream: createStream({level: 'info', transport})
        });
        const provider = new YqlProvider({
            logger,
            token: 'token'
        });

        nock(YQL_HOST)
            .post('/api/v2/operations', {
                content: query,
                action: 'RUN',
                type: 'SQLv1'
            })
            .reply(200, {id});

        times(2).forEach((i) => {
            nock(YQL_HOST)
                .get(`/api/v2/operations/${id}/results`)
                .query({
                    filters: 'DATA'
                })
                .reply(200, {
                    status: i !== 1 ? 'RUNNING' : 'COMPLETED'
                });
        });

        await provider.query({
            query,
            checkResultIntervalSeconds: 1
        });

        expect(nock.pendingMocks()).toHaveLength(0);

        expect(logs).toHaveLength(3);
        expect(logs.filter((it) => it.includes(`check result ${id}`))).toHaveLength(2);
        expect(logs.filter((it) => it.includes(`query ${id} completed`))).toHaveLength(1);
    });

    it('should abort query by timeout', async () => {
        const id = 'super-id';
        const query = 'select 1';

        const {transport, logs} = createArrayTransport();
        const logger = new Logger({
            name: 'test_logger',
            commonMeta: {version: 'unknown', env: 'unknown'},
            stream: createStream({level: 'info', transport})
        });
        const provider = new YqlProvider({
            logger,
            token: 'token'
        });

        nock(YQL_HOST)
            .post('/api/v2/operations', {
                content: query,
                action: 'RUN',
                type: 'SQLv1'
            })
            .reply(200, {
                id: 'super-id'
            });

        nock(YQL_HOST)
            .post(`/api/v2/operations/${id}`, {
                action: 'ABORT'
            })
            .reply(200, {id});

        times(4).forEach((i) => {
            nock(YQL_HOST)
                .get(`/api/v2/operations/${id}/results`)
                .query({
                    filters: 'DATA'
                })
                .reply(200, {
                    status: i === 3 ? 'ABORTED' : 'RUNNING'
                });
        });

        await provider.query({
            query,
            requestTimeoutSeconds: 2,
            checkResultIntervalSeconds: 1
        });

        expect(nock.pendingMocks()).toHaveLength(0);

        expect(logs).toHaveLength(5);
        expect(logs.filter((it) => it.includes(`check result ${id}`))).toHaveLength(4);
        expect(logs.filter((it) => it.includes(`query ${id} rejected with status 'ABORTED'`))).toHaveLength(1);
    });
});

function createArrayTransport({logs = []}: {logs?: string[]} = {}) {
    const writer = (message: string) => logs.push(message);
    const formatTaxi = taxiFormatter();
    const transport: Transport = (report) => writer(stringifyTskv(formatTaxi(report)));

    return {logs, transport, writer};
}
