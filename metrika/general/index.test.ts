import { Server } from 'http';
import express, { Request, Response, NextFunction } from 'express';
import got from 'got';
import { pick } from 'lodash';

import { continuationRequest } from 'server/middlewares/continuation-request';
import { outgoingRequestsLogger } from '.';
import { runServer } from 'server/test-utils/run-server';
import { getServer } from 'server/test-utils/simple-server';
import { requestsMiddleware } from 'server/test-utils/requests-middleware';

const app = express();
app.use([continuationRequest, outgoingRequestsLogger]);

let mockServerEndpoint = '';
let mockServer: Server;
let appServerEndpoint = '';
let appServer: Server;
beforeAll(() => {
    return Promise.all([runServer(getServer()), runServer(app)]).then(
        ([incomingMockServer, incomingAppServer]) => {
            mockServer = incomingMockServer.server;
            mockServerEndpoint = `http://localhost:${incomingMockServer.address.port}`;

            appServer = incomingAppServer.server;
            appServerEndpoint = `http://localhost:${incomingAppServer.address.port}`;
        },
    );
});

afterAll(() => {
    return Promise.all([
        // todo promisify почему то не работает
        new Promise((resolve) => {
            mockServer.close(resolve);
        }),
        new Promise((resolve) => {
            appServer.close(resolve);
        }),
    ]);
});

function stopInterceptMiddleware(
    req: Request,
    res: Response,
    next: NextFunction,
) {
    req.stopOutgoingRequestLogging();
    next();
}

function getLogsMiddleware(req: Request, res: Response) {
    res.status(200).json(pick(req.getOutgoingRequests(), 'logs'));
}

describe('outgoing-request-middleware', () => {
    it('intercepts http requests', () => {
        const testPath = '/intercepts_http_requests';
        app.get(
            testPath,
            requestsMiddleware({
                endpoint: mockServerEndpoint,
                urls: [{ path: '/success' }, { path: '/error' }],
            }),
            getLogsMiddleware,
        );
        return got(`${appServerEndpoint}${testPath}`, { json: true }).then(
            (result) => {
                expect(result.body.logs).toHaveLength(2);
                for (const logEntry of result.body.logs) {
                    expect(logEntry.responseBody).toMatchSnapshot();
                }
            },
        );
    });
    it('stop intercepting', () => {
        const testPath = '/stop_intercepting';
        app.get(
            testPath,
            requestsMiddleware({
                endpoint: mockServerEndpoint,
                urls: [{ path: '/success' }, { path: '/error' }],
            }),
            stopInterceptMiddleware,
            requestsMiddleware({
                endpoint: mockServerEndpoint,
                urls: [{ path: '/success' }, { path: '/error' }],
            }),
            getLogsMiddleware,
        );

        return got(`${appServerEndpoint}${testPath}`, { json: true }).then(
            (result) => {
                expect(result.body.logs).toHaveLength(0);
            },
        );
    });
    it('properly handle parallel requests', () => {
        const testPath = '/properly_handle_parallel_requests';
        const testPath1 = `${testPath}_1`;

        app.get(
            testPath1,
            requestsMiddleware({
                endpoint: mockServerEndpoint,
                urls: [
                    { path: '/success/1' },
                    { path: '/error/1' },
                    [
                        { path: '/success/1?timeout=1000' },
                        { path: '/success/1' },
                    ],
                ],
            }),
            getLogsMiddleware,
        );

        const testPath2 = `${testPath}_2`;
        app.get(
            testPath2,
            requestsMiddleware({
                endpoint: mockServerEndpoint,
                urls: [
                    { path: '/success/2?timeout=1000' },
                    { path: '/error/2' },
                    { path: '/success/2' },
                ],
            }),
            getLogsMiddleware,
        );

        return Promise.all([
            got(`${appServerEndpoint}${testPath1}`, { json: true }),
            got(`${appServerEndpoint}${testPath2}`, { json: true }),
        ]).then(([first, second]) => {
            expect(first.body.logs).toHaveLength(4);
            expect(second.body.logs).toHaveLength(3);

            for (const logEntry of first.body.logs) {
                const { pathname } = new URL(logEntry.url);
                expect(pathname.endsWith('/1')).toBeTruthy();
            }
        });
    });
    it('handle redirects', () => {
        const testPath = '/handle_redirects';

        app.get(
            testPath,
            requestsMiddleware({
                endpoint: mockServerEndpoint,
                urls: [{ path: '/redirect/success' }],
            }),
            getLogsMiddleware,
        );

        return got(`${appServerEndpoint}${testPath}`, { json: true }).then(
            ({ body }) => {
                expect(body.logs).toHaveLength(2);
                expect(body.logs[0].status).toBe('redirect');
                expect(body.logs[1].status).toBe('success');
            },
        );
    });
});
