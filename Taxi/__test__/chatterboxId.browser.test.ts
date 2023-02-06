import {encode} from 'querystring';

import {CHATTERBOX_ID_KEY, STORAGE_PREFIX} from '_pkg/constants/application';
import {BaseHttpAPI} from '_pkg/isomorphic/api';
import {mockRequest} from '_pkg/isomorphic/utils/mockRequest';
import {SessionStorage} from '_pkg/utils/browserStorage';

import {chatterboxIdWrapper} from '../middlewares/chatterboxId';

const HOST = '/host';
const PATH = '/';

const api = new BaseHttpAPI({
    baseURL: HOST,
    middlewares: [chatterboxIdWrapper]
});

window.XMLHttpRequest = mockRequest;

describe('chatterboxId', () => {
    describe('browser', () => {
        const storage = new SessionStorage(STORAGE_PREFIX);

        beforeEach(() => {
            storage.clear();
        });

        test('добавляет chatterboxId в query параметры, если он есть в sessionStorage', async () => {
            storage.set(CHATTERBOX_ID_KEY, 'chatterbox_id');

            const fetch = mockRequest
                .addMock('get', HOST)
                .addResponse({}, 200);

            await api.get(PATH, {
                param1: 'foo'
            });

            expect(fetch.getCalls()[0].url).toBe(`${HOST}${PATH}?${encode({
                param1: 'foo',
                [CHATTERBOX_ID_KEY]: 'chatterbox_id'
            })}`);
        });

        test('не добавляет chatterboxId в query параметры, если он отсутствует в sessionStorage', async () => {
            const fetch = mockRequest
                .addMock('get', HOST)
                .addResponse({}, 200);

            await api.get(PATH, {
                param1: 'foo'
            });

            expect(fetch.getCalls()[0].url).toBe(`${HOST}${PATH}?${encode({
                param1: 'foo'
            })}`);
        });
    });
});
