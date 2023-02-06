import config from '_pkg/config';
import {mockRequest} from '_pkg/isomorphic/utils/mockRequest';
import {normalizeUrl} from '_pkg/isomorphic/utils/url';
import {ApiSource} from '_types/common/api';

import {CSRF_TOKEN_ERROR_CODES, CSRF_URL, csrfWrapper, MAX_CSRF_RETRIES} from '../middlewares/csrf';
import {getAliasBySource} from '../utils';

window.XMLHttpRequest = mockRequest;

describe('csrfWrapper', () => {
    describe('browser', () => {
        beforeEach(() => {
            // @ts-ignore
            delete config.sessionCsrfToken;
        });

        test('csrfWrapper - перезапрашивает токен, но не более MAX_CSRF_RETRIES раз', async () => {
            const fetchCsrf = mockRequest
                .addMock('get', `${getAliasBySource(ApiSource.Internal)}/${CSRF_URL}`)
                .addResponse({csrf_token: 'token'}, 200, 0, 100);

            const fetchResource = mockRequest
                .addMock('get', '/user')
                .addResponse({
                    code: CSRF_TOKEN_ERROR_CODES[1]
                }, 401, 0, 100);

            const {default: fetch} = await import('_pkg/isomorphic/api/fetch');
            const fetchWithCsrf = csrfWrapper(fetch);

            try {
                await fetchWithCsrf('', '/user', {
                    method: 'get'
                });
            } catch {
                // ignore
            }

            expect(fetchResource.getCalls().length).toBe(MAX_CSRF_RETRIES + 1);
            expect(fetchCsrf.getCalls().length).toBe(MAX_CSRF_RETRIES);
        });

        test('csrfWrapper - запрашивает токен единожды для группы запросов', async () => {
            const fetchCsrf = mockRequest
                .addMock('get', `${getAliasBySource(ApiSource.Internal)}/${CSRF_URL}`)
                .addResponse({csrf_token: 'token'}, 200, 50, 100);

            const fetchResource1 = mockRequest.addMock('get', '/endpoint1')
                .addResponse({
                    code: CSRF_TOKEN_ERROR_CODES[1]
                }, 401, 5)
                .addResponse({}, 200, 5);

            const fetchResource2 = mockRequest.addMock('get', '/endpoint2')
                .addResponse({
                    code: CSRF_TOKEN_ERROR_CODES[1]
                }, 401, 5)
                .addResponse({}, 200, 5);

            const fetchResource3 = mockRequest.addMock('get', '/endpoint3')
                .addResponse({
                    code: CSRF_TOKEN_ERROR_CODES[1]
                }, 401, 5)
                .addResponse({}, 200, 5);

            const {default: fetch} = await import('_pkg/isomorphic/api/fetch');
            const fetchWithCsrf = csrfWrapper(fetch);

            await Promise.all([
                fetchWithCsrf('', '/endpoint1', {method: 'get'}),
                fetchWithCsrf('', '/endpoint2', {method: 'get'}),
                fetchWithCsrf('', '/endpoint3', {method: 'get'})
            ]);

            expect(fetchResource1.getCalls().length).toBe(2);
            expect(fetchResource1.getCalls()[0].url).toBe(normalizeUrl('/endpoint1'));
            expect(fetchResource1.getCalls()[1].url).toBe(`${normalizeUrl('/endpoint1')}?csrf_token=token`);

            expect(fetchResource2.getCalls().length).toBe(2);
            expect(fetchResource3.getCalls().length).toBe(2);
            expect(fetchCsrf.getCalls().length).toBe(1);
        });
    });
});
