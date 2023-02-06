import { Server } from 'http';

import express, { Request, Response, NextFunction } from 'express';
import got from 'got';
import { pick } from 'lodash';

import { runServer, getServer, requestsMiddleware } from 'server/utils';

import { outgoingRequestsLogger, ExtendedLogEntry } from '..';

const app = express();
app.use([outgoingRequestsLogger()]);

let mockServerEndpoint = '';
let mockServer: Server;
let appServerEndpoint = '';
let appServer: Server;
beforeAll(async () => {
    return Promise.all([runServer(getServer()), runServer(app)]).then(
        ([incomingMockServer, incomingAppServer]) => {
            mockServer = incomingMockServer.server;
            mockServerEndpoint = incomingMockServer.url;

            appServer = incomingAppServer.server;
            appServerEndpoint = incomingAppServer.url;
        },
    );
});

afterAll(async () => {
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
    req.outgoingRequestLogger?.stop();
    next();
}

function getLogsMiddleware(req: Request, res: Response) {
    res.status(200).json(pick(req.outgoingRequestLogger?.get(), 'logs'));
}

describe('outgoing-request-middleware', () => {
    it('intercepts http requests', async () => {
        const testPath = '/intercepts_http_requests';
        app.get(
            testPath,
            requestsMiddleware({
                endpoint: mockServerEndpoint,
                urls: [{ path: '/success' }, { path: '/error' }],
            }),
            getLogsMiddleware,
        );
        return got<{ logs: ExtendedLogEntry[] }>(
            `${appServerEndpoint}${testPath}`,
            { responseType: 'json' },
        ).then((result) => {
            expect(result.body.logs).toHaveLength(2);
            for (const logEntry of result.body.logs) {
                expect(logEntry.responseBody).toMatchSnapshot();
            }
        });
    });
    it('stop intercepting', async () => {
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

        return got<{ logs: ExtendedLogEntry[] }>(
            `${appServerEndpoint}${testPath}`,
            { responseType: 'json' },
        ).then((result) => {
            expect(result.body.logs).toHaveLength(0);
        });
    });
    it('properly handle parallel requests', async () => {
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
            got<{ logs: ExtendedLogEntry[] }>(
                `${appServerEndpoint}${testPath1}`,
                { responseType: 'json' },
            ),
            got<{ logs: ExtendedLogEntry[] }>(
                `${appServerEndpoint}${testPath2}`,
                { responseType: 'json' },
            ),
        ]).then(([first, second]) => {
            expect(first.body.logs).toHaveLength(4);
            expect(second.body.logs).toHaveLength(3);

            for (const logEntry of first.body.logs) {
                const { pathname } = new URL(logEntry.url);
                expect(pathname.endsWith('/1')).toBeTruthy();
            }
        });
    });
    it('handle redirects', async () => {
        const testPath = '/handle_redirects';

        app.get(
            testPath,
            requestsMiddleware({
                endpoint: mockServerEndpoint,
                urls: [{ path: '/redirect/success' }],
            }),
            getLogsMiddleware,
        );

        return got<{ logs: ExtendedLogEntry[] }>(
            `${appServerEndpoint}${testPath}`,
            { responseType: 'json' },
        ).then(({ body }) => {
            expect(body.logs).toHaveLength(2);
            expect(body.logs[0].status).toBe('redirect');
            expect(body.logs[1].status).toBe('success');
        });
    });
});
