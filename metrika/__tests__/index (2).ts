import http, { Server } from 'http';
import { Readable } from 'stream';

import got from 'got';
import { omit } from 'lodash';

import { runServer, getServer } from 'server/utils';

import { start, stop } from '..';

let mockServerEndpoint = '';
let mockServer: Server;
beforeAll(async () => {
    return runServer(getServer()).then((incomingMockServer) => {
        mockServer = incomingMockServer.server;
        mockServerEndpoint = incomingMockServer.url;
    });
});

afterAll(async () => {
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
            'requestHeaders',
            'responseHeaders.date',
            'responseHeaders.etag',
            'url',
            'timings',
        ]);
        return element;
    });
}

describe('http-intercept', () => {
    it('works', async () => {
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
        it('via .write', async () => {
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
                                .on('data', () => {}) // eslint-disable-line @typescript-eslint/no-empty-function
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
        it('via .end', async () => {
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
                                .on('data', () => {}) // eslint-disable-line @typescript-eslint/no-empty-function
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
        it('via .write and .end', async () => {
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
                                .on('data', () => {}) // eslint-disable-line @typescript-eslint/no-empty-function
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
    it('supports stream', async () => {
        const collectedData: any[] = [];
        start((data: any) => {
            collectedData.push(data);
        });

        const readable = new Readable();
        const promise = got.post(`${mockServerEndpoint}/success`, {
            ...options,
            body: readable,
        });
        readable.push('Hello there!');
        readable.push(null);

        return promise.then(() => {
            stop();
            expect(omitHeaders(collectedData)).toMatchSnapshot();
        });
    });
    it('respects `shouldRecord` property', async () => {
        const collectedData: any[] = [];
        start(
            (data: any) => {
                collectedData.push(data);
            },
            {
                shouldRecord: () => false,
            },
        );

        const readable = new Readable();
        const promise = got.post(`${mockServerEndpoint}/success`, {
            ...options,
            body: readable,
        });
        readable.push('Hello there!');
        readable.push(null);

        return promise.then(() => {
            stop();
            expect(omitHeaders(collectedData)).toMatchSnapshot();
        });
    });
    it('respects limits on request body', async () => {
        const collectedData: any[] = [];
        start(
            (data: any) => {
                collectedData.push(data);
            },
            {
                shouldRecordRequestBody: () => false,
            },
        );

        const readable = new Readable();
        const promise = got.post(`${mockServerEndpoint}/success`, {
            ...options,
            body: readable,
        });
        readable.push('Hello there!');
        readable.push(null);

        return promise.then(() => {
            stop();
            expect(omitHeaders(collectedData)).toMatchSnapshot();
        });
    });
    it('respects limits on request body2', async () => {
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
    it('handle big request', async () => {
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

        const length = 10000;
        const text = 'testtext';

        const promise = got.get(
            `${mockServerEndpoint}/chunks/${text}/${length}`,
            {
                ...options,
                responseType: 'text',
            },
        );

        return promise.then(({ body }) => {
            stop();

            expect(body).toHaveLength(length * text.length);
        });
    }, 10000);

    it('collect big request', async () => {
        const collectedData: any[] = [];
        start((data: any) => {
            collectedData.push(data);
        });

        const length = 10000;
        const text = 'testtext';

        const promise = got.get(
            `${mockServerEndpoint}/chunks/${text}/${length}`,
            {
                ...options,
                responseType: 'text',
            },
        );

        return promise.then(({ body }) => {
            stop();
            expect(collectedData[0].responseBody).toEqual(body);
        });
    }, 10000);
});
