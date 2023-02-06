import {createStream, Logger, stringifyTskv, taxiFormatter, Transport} from '@lavka-js-toolbox/logger';
import {delayMs} from '@lavka-js-toolbox/timer';
import express from 'express';
import got from 'got';
import http from 'http';
import {first, last, times} from 'lodash';
import net from 'net';
import nock from 'nock';
import pMap from 'p-map';

import {ExpressHealthHandler, SHUTDOWN_HTTP_STATUS} from './index';

async function startServer(app: express.Application) {
    const server = http.createServer(app);

    await new Promise((resolve) => server.listen(resolve));

    const port = (server.address() as net.AddressInfo).port;
    const host = `http://localhost:${port}`;

    return {server, host};
}

function stopServer(server: http.Server) {
    return new Promise<void>((resolve) => server.close(() => resolve()));
}

describe('package "express-health-handler"', () => {
    jest.setTimeout(5000);

    let app: express.Application;
    let server: http.Server;
    let host: string;
    let logger: Logger;
    let logs: string[];

    beforeAll(async () => {
        nock.disableNetConnect();
        nock.enableNetConnect(/localhost/);
    });

    afterAll(async () => {
        nock.enableNetConnect();
    });

    beforeEach(async () => {
        app = express().get('/delay', (_, res) => {
            void delayMs(1000).then(() => res.end());
        });

        const result = await startServer(app);

        server = result.server;
        host = result.host;

        const {transport, logs: logArr} = createArrayTransport();
        logs = logArr;

        logger = new Logger({
            name: 'test_logger',
            commonMeta: {version: 'unknown', env: 'unknown'},
            stream: createStream({level: 'info', transport})
        });
    });

    afterEach(async () => {
        nock.cleanAll();

        await stopServer(server);
    });

    it('should return shutdown status on /ping', async () => {
        const handler = new ExpressHealthHandler({
            logger,
            shutdownDelay: 100,
            httpTerminationTimeout: 5000,
            checkConnectionsCountInterval: 300,
            server,
            app
        });

        // Запускаем долгий запрос, чтобы сервер сразу не выключился
        void got.get(`${host}/delay`);

        const ping: number[] = [];

        // Имитируем запросы ping-ов
        void pMap(
            times(10),
            async () => {
                const {statusCode} = await got.get(`${host}/ping`, {
                    throwHttpErrors: false
                });

                ping.push(statusCode);

                await delayMs(100);
            },
            {concurrency: 1}
        );

        // Даем возможность ping-ам получить положительные статусы до shutdown
        await delayMs(500);
        await handler.shutdown();

        expect(first(ping)).toBe(200);
        expect(last(ping)).toBe(SHUTDOWN_HTTP_STATUS);

        expect(first(logs)).toMatch(/Shutdown started, all active connections will be closed in 5\.1 seconds/gim);
        expect(last(logs)).toMatch(/Successfully terminated http/gim);

        expect(logs.find((it) => it.includes('Server has 1 active http connections'))).not.toBeFalsy();
        expect(logs.find((it) => it.includes('Server has 0 active http connections'))).not.toBeFalsy();
    });

    it('should wait until all connections will close', async () => {
        const handler = new ExpressHealthHandler({
            logger,
            shutdownDelay: 100,
            httpTerminationTimeout: 5000,
            checkConnectionsCountInterval: 300,
            server,
            app
        });

        times(3).forEach(() => void got.get(`${host}/delay`));

        await handler.shutdown();

        expect(first(logs)).toMatch(/Shutdown started, all active connections will be closed in 5\.1 seconds/gim);
        expect(last(logs)).toMatch(/Successfully terminated http/gim);

        expect(logs.find((it) => it.includes('Server has 3 active http connections'))).not.toBeFalsy();
        expect(logs.find((it) => it.includes('Server has 0 active http connections'))).not.toBeFalsy();
    });

    it('should have delay for removing instance from balancer', async () => {
        const handler = new ExpressHealthHandler({
            logger,
            shutdownDelay: 1500,
            httpTerminationTimeout: 2000,
            checkConnectionsCountInterval: 100,
            server,
            app
        });

        await handler.shutdown();

        const start = logs.find((it) => it.includes('Shutdown started')) || '';
        const end = logs.find((it) => it.includes('Server has 0 active http connections')) || '';

        const startTimestamp = new Date(/timestamp=([^\t]+)/gim.exec(start)?.[1] || '').getTime();
        const endTimestamp = new Date(/timestamp=([^\t]+)?/gim.exec(end)?.[1] || '').getTime();

        expect(endTimestamp - startTimestamp).toBeGreaterThanOrEqual(1000);
        expect(endTimestamp - startTimestamp).toBeLessThanOrEqual(2000);
    });

    it('should not shutdown more than once', async () => {
        const handler = new ExpressHealthHandler({
            logger,
            shutdownDelay: 100,
            httpTerminationTimeout: 1000,
            server,
            app
        });

        await Promise.all([handler.shutdown(), handler.shutdown(), handler.shutdown()]);

        expect(logs.filter((it) => it.includes('Shutdown started'))).toHaveLength(1);
        expect(logs.filter((it) => it.includes('Server is already shutting down'))).toHaveLength(2);
    });

    it('should close all connections if timeout', async () => {
        const handler = new ExpressHealthHandler({
            logger,
            shutdownDelay: 100,
            httpTerminationTimeout: 500,
            checkConnectionsCountInterval: 350,
            server,
            app
        });

        void got.get(`${host}/delay`);

        await handler.shutdown();

        expect(first(logs)).toMatch(/Shutdown started, all active connections will be closed in 0\.6 seconds/gim);
        expect(last(logs)).toMatch(
            /Timeout waiting for closing active connections, force terminate express: Timeout on terminate express/gim
        );

        expect(logs.filter((it) => it.includes('Server has 1 active http connections'))).toHaveLength(1);
        expect(logs.filter((it) => it.includes('Server has 0 active http connections'))).toHaveLength(0);
    });

    it('should shutdown if application memory out', async () => {
        new ExpressHealthHandler({
            logger,
            shutdownDelay: 100,
            httpTerminationTimeout: 3000,
            healthCheckInterval: 100,
            checkConnectionsCountInterval: 500,
            memoryLimit: 0,
            server,
            app
        });

        // Запускаем долгий запрос, чтобы сервер сразу не выключился
        void got.get(`${host}/delay`);
        await delayMs(3000);

        expect(logs[0]).toMatch(/Memory consumption: \[.+\/0.0\]gb/gim);
        expect(logs[1]).toMatch(/Out of memory: shutting down now!/gim);
        expect(logs[2]).toMatch(/Shutdown started, all active connections will be closed in 3\.1 seconds/gim);
        expect(logs[3]).toMatch(/Server has 1 active http connections/gim);
        expect(logs[4]).toMatch(/Server has 0 active http connections/gim);
        expect(logs[5]).toMatch(/Successfully terminated http/gim);
    });

    it('should use hook for ping status and not override shutdown status', async () => {
        const handler = new ExpressHealthHandler({
            logger,
            shutdownDelay: 100,
            httpTerminationTimeout: 5000,
            checkConnectionsCountInterval: 300,
            server,
            app,
            hooks: {
                beforePing: async () => {
                    await delayMs(100);
                    return {statusCode: 400};
                }
            }
        });

        // Запускаем долгий запрос, чтобы сервер сразу не выключился
        void got.get(`${host}/delay`);

        const pingStatus: number[] = [];

        void pMap(
            times(10),
            async () => {
                const {statusCode} = await got.get(`${host}/ping`, {
                    throwHttpErrors: false
                });

                pingStatus.push(statusCode);
            },
            {concurrency: 1}
        );

        // Даем возможность ping-ам получить положительные статусы до начала выключения сервера
        await delayMs(500);
        await handler.shutdown();

        expect(first(pingStatus)).toBe(400);
        expect(last(pingStatus)).toBe(SHUTDOWN_HTTP_STATUS);

        expect(first(logs)).toMatch(/Shutdown started, all active connections will be closed in 5\.1 seconds/gim);
        expect(last(logs)).toMatch(/Successfully terminated http/gim);

        expect(logs.find((it) => it.includes('Server has 1 active http connections'))).not.toBeFalsy();
        expect(logs.find((it) => it.includes('Server has 0 active http connections'))).not.toBeFalsy();
    });

    it('should use hook after shutdown started', async () => {
        let isHookCalled = false;

        const handler = new ExpressHealthHandler({
            logger,
            shutdownDelay: 100,
            httpTerminationTimeout: 1000,
            server,
            app,
            hooks: {
                beforeShutdownStart: () => {
                    isHookCalled = true;
                }
            }
        });

        await handler.shutdown();

        expect(isHookCalled).toBe(true);
    });
});

function createArrayTransport({logs = []}: {logs?: string[]} = {}) {
    const writer = (message: string) => logs.push(message);
    const formatTaxi = taxiFormatter();
    const transport: Transport = (report) => writer(stringifyTskv(formatTaxi(report)));

    return {logs, transport, writer};
}
