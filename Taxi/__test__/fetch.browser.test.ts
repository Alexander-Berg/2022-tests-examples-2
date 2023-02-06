import {AuthError, ForbiddenError, NotFoundError, ServerError, TimeoutError} from '../../errors';
import {mockRequest} from '../../utils/mockRequest';
import fetch from '../fetch';

window.XMLHttpRequest = mockRequest;
const TEST_URL = '/test';

describe('utils/httpApi/fetch', () => {
    describe('browser', () => {
        beforeEach(() => {
            mockRequest.clear();
        });

        test('get answer', async () => {
            const response = {xxx: 1};

            mockRequest.addMock('get', TEST_URL)
                .addResponse(response, 200);

            const res = await fetch('', TEST_URL, {
                method: 'get'
            });

            expect(res).toEqual(response);
        });

        test('responseType undefined by default', async () => {
            const {default: fetch} = await import('../fetch');
            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 200);

            const response = await fetch('', TEST_URL, {
                method: 'get',
                responseMapper: ({res}) => res
            });

            expect(response.config.responseType).toEqual(undefined);
        });

        test('change responseType', async () => {
            const {default: fetch} = await import('../fetch');
            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 200);

            const response = await fetch('', TEST_URL, {
                method: 'get',
                responseMapper: ({res}) => res,
                responseType: 'json'
            });

            expect(response.config.responseType).toEqual('json');
        });

        test('timeout', async () => {
            const timeout = 1;

            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 404, timeout * 20);

            try {
                await fetch('', TEST_URL, {
                    method: 'get',
                    timeout
                });
            } catch (e) {
                expect(e instanceof TimeoutError).toBe(true);
                return;
            }

            throw new Error('Unexpected error');
        });

        test('401', async () => {
            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 401);

            try {
                await fetch('', TEST_URL, {
                    method: 'get'
                });
            } catch (e) {
                expect(e instanceof AuthError).toBe(true);
                return;
            }

            throw new Error('Unexpected error');
        });

        test('404', async () => {
            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 404);

            try {
                await fetch('', TEST_URL, {
                    method: 'get'
                });
            } catch (e) {
                expect(e instanceof NotFoundError).toBe(true);
                return;
            }

            throw new Error('Unexpected error');
        });

        test('403', async () => {
            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 403);

            try {
                await fetch('', TEST_URL, {
                    method: 'get'
                });
            } catch (e) {
                expect(e instanceof ForbiddenError).toBe(true);
                return;
            }

            throw new Error('Unexpected error');
        });

        test('other errors', async () => {
            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 500);

            try {
                await fetch('', TEST_URL, {
                    method: 'get'
                });
            } catch (e) {
                expect(e instanceof ServerError).toBe(true);
                return;
            }

            throw new Error('Unexpected error');
        });

        test('remove undefined from querystring', async () => {
            const mock = mockRequest.addMock('get', `host/${TEST_URL}`)
                .addResponse({}, 200);

            await fetch('host', TEST_URL, {
                method: 'get',
                query: {
                    prop1: 1,
                    prop2: undefined,
                    prop3: 3
                }
            });

            expect(mock.getCalls()[0].url).toBe(`host${TEST_URL}/?prop1=1&prop3=3`);
        });

        test('remove undefined from headers', async () => {
            const mock = mockRequest.addMock('get', `host/${TEST_URL}`)
                .addResponse({}, 200);

            await fetch('host', TEST_URL, {
                method: 'get',
                headers: {
                    prop1: '1',
                    prop2: undefined!,
                    prop3: '3'
                }
            });

            expect(mock.getCalls()[0].headers?.filter(h => h[1] === undefined).length).toBe(0);
        });

        test('serialize querystring', async () => {
            const mock = mockRequest.addMock('get', `host${TEST_URL}`)
                .addResponse({}, 200);

            await fetch('host', TEST_URL, {
                method: 'get',
                query: {
                    prop1: '1',
                    prop2: [0, 1, 2],
                    prop3: '/2/'
                }
            });

            expect(mock.getCalls()[0].url).toBe(
                `host${TEST_URL}/?prop1=1&prop2=0&prop2=1&prop2=2&prop3=${encodeURIComponent('/2/')}`
            );
        });
    });
});
