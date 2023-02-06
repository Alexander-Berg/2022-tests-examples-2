import { Readable } from 'stream';
import http, { Server } from 'http';
import toReadableStream from 'to-readable-stream';
import { omit } from 'lodash';
import { start, stop } from '..';
import got from 'got';
import { runServer } from 'server/test-utils/run-server';
import { getServer } from 'server/test-utils/simple-server';

let mockServerEndpoint = '';
let mockServer: Server;
beforeAll(() => {
    return runServer(getServer()).then((incomingMockServer) => {
        mockServer = incomingMockServer.server;
        mockServerEndpoint = `http://localhost:${incomingMockServer.address.port}`;
    });
});

afterAll(() => {
    return Promise.all([
        // todo promisify почему то не работает
        new Promise((resolve) => {
            mockServer.close(resolve);
        }),
    ]);
});

const options = {
    throwHttpErrors: false,
    retry: 0,
};

function omitHeaders(data: any) {
    return data.map((incomingElement: any) => {
        const element = omit(incomingElement, [
            'requestHeaders.host',
            'requestHeaders.user-agent',
            'responseHeaders.date',
            'responseHeaders.etag',
            'url',
            'timings',
        ]);
        return element;
    });
}

describe('http-intercept', () => {
    it('works', () => {
        const collectedData: any[] = [];
        start((data: any) => {
            collectedData.push(data);
        });

        return got(`${mockServerEndpoint}/success`, options as any)
            .then(() => got(`${mockServerEndpoint}/error`, options as any))
            .then(() => {
                expect(omitHeaders(collectedData)).toMatchSnapshot();
                stop();
            });
    });
    describe('records request body', () => {
        it('via .write', () => {
            const collectedData: any[] = [];
            start((data: any) => {
                collectedData.push(data);
            });

            return new Promise((resolve, reject) => {
                const request = http
                    .request(
                        `${mockServerEndpoint}/success`,
                        { method: 'POST' },
                        (response) => {
                            response
                                .on('data', () => {})
                                .on('end', resolve)
                                .on('error', reject);
                        },
                    )
                    .on('error', reject);

                request.write('Hello there!');
                request.end();
            }).then(() => {
                stop();
                expect(omitHeaders(collectedData)).toMatchSnapshot();
            });
        });
        it('via .end', () => {
            const collectedData: any[] = [];
            start((data: any) => {
                collectedData.push(data);
            });

            return new Promise((resolve, reject) => {
                const request = http
                    .request(
                        `${mockServerEndpoint}/success`,
                        { method: 'POST' },
                        (response) => {
                            response
                                .on('data', () => {})
                                .on('end', resolve)
                                .on('error', reject);
                        },
                    )
                    .on('error', reject);

                request.end('Hello there!');
            }).then(() => {
                stop();
                expect(omitHeaders(collectedData)).toMatchSnapshot();
            });
        });
        it('via .write and .end', () => {
            const collectedData: any[] = [];
            start((data: any) => {
                collectedData.push(data);
            });

            return new Promise((resolve, reject) => {
                const request = http
                    .request(
                        `${mockServerEndpoint}/success`,
                        { method: 'POST' },
                        (response) => {
                            response
                                .on('data', () => {})
                                .on('end', resolve)
                                .on('error', reject);
                        },
                    )
                    .on('error', reject);

                request.end('Hello there');
                request.end(' and there!');
            }).then(() => {
                stop();
                expect(omitHeaders(collectedData)).toMatchSnapshot();
            });
        });
    });
    it('supports stream', () => {
        const collectedData: any[] = [];
        start((data: any) => {
            collectedData.push(data);
        });

        const promise = got.post(`${mockServerEndpoint}/success`, {
            ...options,
            body: toReadableStream('Hello there!'),
        });

        return promise.then(() => {
            stop();
            expect(omitHeaders(collectedData)).toMatchSnapshot();
        });
    });
    it('respects `shouldRecord` property', () => {
        const collectedData: any[] = [];
        start(
            (data: any) => {
                collectedData.push(data);
            },
            {
                shouldRecord: () => false,
            },
        );

        const promise = got.post(`${mockServerEndpoint}/success`, {
            ...options,
            body: toReadableStream('Hello there!'),
        });

        return promise.then(() => {
            stop();
            expect(omitHeaders(collectedData)).toMatchSnapshot();
        });
    });
    it('respects limits on request body', () => {
        const collectedData: any[] = [];
        start(
            (data: any) => {
                collectedData.push(data);
            },
            {
                shouldRecordRequestBody: () => false,
            },
        );

        const promise = got.post(`${mockServerEndpoint}/success`, {
            ...options,
            body: toReadableStream('Hello there!'),
        });

        return promise.then(() => {
            stop();
            expect(omitHeaders(collectedData)).toMatchSnapshot();
        });
    });
    it('respects limits on request body2', () => {
        const collectedData: any[] = [];
        start(
            (data: any) => {
                collectedData.push(data);
            },
            {
                shouldRecordRequestBody: (_, currentLength, chunkLength) => {
                    return currentLength + chunkLength < 10;
                },
            },
        );

        const readable = new Readable();
        const promise = got.post(`${mockServerEndpoint}/success`, {
            ...options,
            body: readable,
        });
        readable.push('Hello ');
        readable.push('there!');
        readable.push(null);

        return promise.then(() => {
            stop();
            expect(omitHeaders(collectedData)).toMatchSnapshot();
        });
    });
});
