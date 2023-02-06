import nock from 'nock';

import {AuthError, ForbiddenError, NotFoundError, ServerError, TimeoutError} from '../../errors';

describe('utils/httpApi/fetch', () => {
    describe('node', () => {
        const fakeHost = 'http://test.fake.ru';
        const fakeEndpoint = '/test/';
        window.XMLHttpRequest = undefined!;

        test('get answer', async () => {
            const {default: fetch} = await import('../fetch');

            const response = {xxx: 1};
            nock(fakeHost).get(fakeEndpoint).reply(200, response);

            const res = await fetch(fakeHost, fakeEndpoint, {
                method: 'get'
            });

            expect(res).toEqual(response);
        });

        test('responseType undefined by default', async () => {
            const {default: fetch} = await import('../fetch');
            nock(fakeHost).get(fakeEndpoint).reply(200);

            const response = await fetch(fakeHost, fakeEndpoint, {
                method: 'get',
                responseMapper: ({res}) => res
            });

            expect(response.config.responseType).toEqual(undefined);
        });

        test('change responseType', async () => {
            const {default: fetch} = await import('../fetch');
            nock(fakeHost).get(fakeEndpoint).reply(200);

            const response = await fetch(fakeHost, fakeEndpoint, {
                method: 'get',
                responseMapper: ({res}) => res,
                responseType: 'json'
            });

            expect(response.config.responseType).toEqual('json');
        });

        test('timeout', async () => {
            const {default: fetch} = await import('../fetch');
            const timeout = 1;

            nock(fakeHost).get(fakeEndpoint).delayConnection(timeout * 20).reply(200);

            try {
                await fetch(fakeHost, fakeEndpoint, {
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
            const {default: fetch} = await import('../fetch');
            nock(fakeHost).get(fakeEndpoint).reply(401);

            try {
                await fetch(fakeHost, fakeEndpoint, {
                    method: 'get'
                });
            } catch (e) {
                expect(e instanceof AuthError).toBe(true);
                return;
            }

            throw new Error('Unexpected error');
        });

        test('404', async () => {
            const {default: fetch} = await import('../fetch');
            nock(fakeHost).get(fakeEndpoint).reply(404);

            try {
                await fetch(fakeHost, fakeEndpoint, {
                    method: 'get'
                });
            } catch (e) {
                expect(e instanceof NotFoundError).toBe(true);
                return;
            }

            throw new Error('Unexpected error');
        });

        test('403', async () => {
            const {default: fetch} = await import('../fetch');
            nock(fakeHost).get(fakeEndpoint).reply(403);

            try {
                await fetch(fakeHost, fakeEndpoint, {
                    method: 'get'
                });
            } catch (e) {
                expect(e instanceof ForbiddenError).toBe(true);
                return;
            }

            throw new Error('Unexpected error');
        });

        test('other errors', async () => {
            const {default: fetch} = await import('../fetch');
            nock(fakeHost).get(fakeEndpoint).reply(500);

            try {
                await fetch(fakeHost, fakeEndpoint, {
                    method: 'get'
                });
            } catch (e) {
                expect(e instanceof ServerError).toBe(true);
                return;
            }

            throw new Error('Unexpected error');
        });

        test('remove undefined from querystring', async () => {
            const {default: fetch} = await import('../fetch');

            let path: string | undefined;
            nock(fakeHost).get(fakeEndpoint).query(true).reply(200, function () {
                path = this.req.path;
                return {};
            });

            await fetch(fakeHost, fakeEndpoint, {
                method: 'get',
                query: {
                    prop1: 1,
                    prop2: undefined,
                    prop3: 3
                }
            });

            expect(path).toBe(`${fakeEndpoint}?prop1=1&prop3=3`);
        });

        test('remove undefined from headers', async () => {
            const {default: fetch} = await import('../fetch');

            let headers: Indexed<string> | undefined;
            nock(fakeHost).get(fakeEndpoint).reply(200, function () {
                headers = this.req.headers;
                return {};
            });

            await fetch(fakeHost, fakeEndpoint, {
                method: 'get',
                headers: {
                    prop1: '1',
                    prop2: undefined!,
                    prop3: '3'
                }
            });

            expect(Object.getOwnPropertyDescriptor(headers, 'prop2')).toBe(undefined);
        });

        test('serialize querystring', async () => {
            const {default: fetch} = await import('../fetch');

            let path: string | undefined;
            nock(fakeHost).get(fakeEndpoint).query(true).reply(200, function () {
                path = this.req.path;
                return {};
            });

            await fetch(fakeHost, fakeEndpoint, {
                method: 'get',
                query: {
                    prop1: '1',
                    prop2: [0, 1, 2],
                    prop3: '/2/'
                }
            });

            expect(path).toBe(
                `${fakeEndpoint}?prop1=1&prop2=0&prop2=1&prop2=2&prop3=${encodeURIComponent('/2/')}`
            );
        });
    });
});
