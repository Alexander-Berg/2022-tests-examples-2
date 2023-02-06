import {encode} from 'querystring';

import config from '_pkg/config';
import {BaseHttpAPI} from '_pkg/isomorphic/api';
import {mockRequest} from '_pkg/isomorphic/utils/mockRequest';

import {experimentFilters} from '../middlewares/experimentFilters';

const HOST = '/host';
const ENDPOINT_IN_EXPERIMENT = '/orders/';
const MATCH_AT_START = '/orders/v1/';
const MATCH_AT_END = '/v1/orders/';
const MATCH_IN_BETWEEN = '/v1/orders/id/';
const EMPTY = '/';

const api = new BaseHttpAPI({
    baseURL: HOST,
    middlewares: [experimentFilters(config.userInfo.filters)]
});

window.XMLHttpRequest = mockRequest;

describe('experimentFilters', () => {
    describe('browser', () => {
        test('experimentFilters - получаем фильтры только для ручек совпадающих с экспериментом', async () => {
            const fetch = mockRequest
                .addMock('get', `${HOST}${ENDPOINT_IN_EXPERIMENT}`)
                .addResponse({}, 200);

            await api.get(ENDPOINT_IN_EXPERIMENT, {
                param1: '1'
            });

            expect(fetch.getCalls()[0].url).toBe(`${HOST}${ENDPOINT_IN_EXPERIMENT}?${encode({
                param1: '1',
                last_orders: 15
            })}`);
        });

        test('experimentFilters - не аффектит ручки совпадающие по началу', async () => {
            const fetch = mockRequest
                .addMock('get', `${HOST}${MATCH_AT_START}`)
                .addResponse({}, 200);

            await api.get(MATCH_AT_START, {
                param1: '1'
            });

            expect(fetch.getCalls()[0].url).toBe(`${HOST}${MATCH_AT_START}?${encode({
                param1: '1'
            })}`);
        });

        test('experimentFilters - не аффектит ручки совпадающие по концу', async () => {
            const fetch = mockRequest
                .addMock('get', `${HOST}${MATCH_AT_END}`)
                .addResponse({}, 200);

            await api.get(MATCH_AT_END, {
                param1: '1'
            });

            expect(fetch.getCalls()[0].url).toBe(`${HOST}${MATCH_AT_END}?${encode({
                param1: '1'
            })}`);
        });

        test('experimentFilters - не аффектит совпадающие внутри', async () => {
            const fetch = mockRequest
                .addMock('get', `${HOST}${MATCH_IN_BETWEEN}`)
                .addResponse({}, 200);

            await api.get(MATCH_IN_BETWEEN, {
                param1: '1'
            });

            expect(fetch.getCalls()[0].url).toBe(`${HOST}${MATCH_IN_BETWEEN}?${encode({
                param1: '1'
            })}`);
        });

        test('experimentFilters - не аффектит индексные ручки', async () => {
            const fetch = mockRequest
                .addMock('get', `${HOST}${EMPTY}`)
                .addResponse({}, 200);

            await api.get(EMPTY, {
                param1: '1'
            });

            expect(fetch.getCalls()[0].url).toBe(`${HOST}${EMPTY}?${encode({
                param1: '1'
            })}`);
        });

        test('experimentFilters - post данные в виде объекта', async () => {
            const fetch = mockRequest
                .addMock('post', `${HOST}${ENDPOINT_IN_EXPERIMENT}`)
                .addResponse({}, 200);

            await api.post(ENDPOINT_IN_EXPERIMENT, {param1: '1'});

            expect(JSON.parse(fetch.getCalls()[0].data)).toEqual({
                param1: '1',
                last_orders: 15
            });
        });

        test('experimentFilters - post данные в виде массива', async () => {
            const fetch = mockRequest
                .addMock('post', `${HOST}${ENDPOINT_IN_EXPERIMENT}`)
                .addResponse({}, 200);

            await api.post(ENDPOINT_IN_EXPERIMENT, [{param1: '1'}, {param1: '2'}]);

            expect(JSON.parse(fetch.getCalls()[0].data)).toEqual([
                {param1: '1'},
                {param1: '2'},
                {last_orders: 15}
            ]);
        });
    });
});
