import { Server } from 'http';

import express from 'express';
import got from 'got';

import { runServer } from 'server/utils';

import { createRpcEndpoint } from '..';

type Express = ReturnType<typeof express>;

let mockServerEndpoint = '';
let mockServer: Server;
let mockExpressApp: Express;
const createEmptyMiddleware = () => jest.fn((_req, _res, next) => next());

describe('rpc', () => {
    beforeEach(async () => {
        return runServer(express().use(express.json())).then(
            (incomingMockServer) => {
                mockServerEndpoint = incomingMockServer.url;
                mockServer = incomingMockServer.server;
                mockExpressApp = (incomingMockServer.originalListener as unknown) as Express;
            },
        );
    });

    afterEach(async () => {
        return new Promise((resolve) => {
            mockServer.close(resolve);
        });
    });

    it('apply middlewares', async () => {
        const middleware = createEmptyMiddleware();

        createRpcEndpoint({
            router: mockExpressApp,
            operations: {},
            endpointUrl: '/rpc',
            middlewares: [middleware],
        });

        await got.post(`${mockServerEndpoint}/rpc/operation`, {
            throwHttpErrors: false,
        });

        expect(middleware.mock.calls.length).toBe(1);
    });
    it('apply middlewares only to rpc route', async () => {
        const middleware = createEmptyMiddleware();

        createRpcEndpoint({
            router: mockExpressApp,
            operations: {},
            endpointUrl: '/rpc',
            middlewares: [middleware],
        });

        mockExpressApp.get('/not-an-rpc', (_req, res) =>
            res.status(200).send('OK'),
        );

        await got.get(`${mockServerEndpoint}/not-an-rpc`);

        expect(middleware.mock.calls.length).toBe(0);
    });
    it('call operation', async () => {
        const operation = jest.fn(async () => []);

        createRpcEndpoint({
            router: mockExpressApp,
            operations: {
                operation,
            },
            endpointUrl: '/rpc',
        });

        const { body } = await got.post(`${mockServerEndpoint}/rpc/operation`, {
            responseType: 'json',
            throwHttpErrors: false,
        });

        expect(operation.mock.calls.length).toBe(1);
        expect(body).toEqual({ result: [] });
    });
});
