import got from 'got';

import {TestServer} from '@/src/tests/unit/test-server';

describe('test server app', () => {
    const testServer = new TestServer();
    let address = '';

    beforeAll(async () => {
        address = await testServer.getAddress();
    });

    afterAll(async () => {
        await testServer.stop();
    });

    it('should redirect on auth page', async () => {
        const {statusCode, headers} = await got.get(`${address}/foo`, {
            throwHttpErrors: false,
            followRedirect: false
        });

        expect(statusCode).toBe(302);
        expect(headers.location?.includes('passport.yandex-team.ru/auth')).toBeTruthy();
    });

    // TODO add region tests:
    // /                -> /ru/products
    // /ru              -> /ru/products
    // /ru/             -> /ru/products
    // /unknown-region  -> NOT FOUND PAGE
    // /unknown-region/ -> NOT FOUND PAGE
    // /ru/not-found    -> NOT FOUND PAGE
});
