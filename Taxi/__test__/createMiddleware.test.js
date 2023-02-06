const { proxyReqBodyDecorator, userResDecorator, createCipherMiddleware } = require('../createCipherMiddleware');
const { StrategyError, ParseBodyError, NoRequiredParametersError } = require('../errors');
const { createStrategyDefiner } = require('../createStrategyDefiner');
const { createSupchatStrategiesMap } = require('../strategies/supchat');

const LOGGER = { error: () => { } };
const HOST = 'https://ya.ru';
const GET_STRATEGY = createStrategyDefiner(createSupchatStrategiesMap());
const MOCK_STRATEGY = {
    encryptRequest: body => { return { ...body, encrypt: true }; },
    decryptResponse: body => { return { ...body, encrypt: false }; }
};

describe('proxyReqBodyDecorator', () => {
    test('proxy request body decorator defines as expected', async () => {
        const result = await proxyReqBodyDecorator({}, MOCK_STRATEGY);

        expect(result.encrypt).toBe(true);
    });

    test('function should return a strategy error', async () => {
        expect(async () => {
            await proxyReqBodyDecorator({}, undefined);
        }).rejects.toThrow(StrategyError);
    });

    test('function should return a ParseBodyError', async () => {
        const stringBody = Buffer.from('asdasfawdqwcw');
        const body = await proxyReqBodyDecorator(stringBody, { encryptRequest: () => { throw new ParseBodyError(); } });

        expect(body).toBe(stringBody);
    });
    test('function should return a NoRequiredParametersError', async () => {
        const invalidBody = { test: 'sdfsdse' };
        const body = await proxyReqBodyDecorator(invalidBody, { encryptRequest: async () => { throw new NoRequiredParametersError(); } });

        expect(body).toEqual(invalidBody);
    });
    test('throw unrecognized error', async () => {
        expect(async () => {
            await proxyReqBodyDecorator(
                {},
                {encryptRequest: async () => { throw new Error(); }}
            );
        }).rejects.toThrow();
    });
});

describe('userResDecorator', () => {
    const PROXY_RES = { statusCode: 200 };

    test('defined as expected', async () => {
        const result = await userResDecorator({}, MOCK_STRATEGY, PROXY_RES);

        expect(result.encrypt).toBe(false);
    });

    test('throw error StrategyError', () => {
        expect(async () => {
            await userResDecorator({}, undefined, PROXY_RES);
        }).rejects.toThrow(StrategyError);
    });

    test('throw error ParseBodyError', async () => {
        const stringBody = Buffer.from('asdasfawdqwcw');
        const body = await userResDecorator(
            stringBody,
            { decryptResponse: () => { throw new ParseBodyError(); } },
            PROXY_RES
        );

        expect(body).toBe(stringBody);
    });
    test('throw error NoRequiredParametersError', async () => {
        const invalidBody = { test: 'sdfsdse' };
        const body = await userResDecorator(
            invalidBody,
            { decryptResponse: async () => { throw new NoRequiredParametersError(); } },
            PROXY_RES
        );

        expect(body).toEqual(invalidBody);
    });

    test('throw unrecognized error', async () => {
        expect(async () => {
            await userResDecorator(
                {},
                {decryptResponse: async () => { throw new Error(); }},
                PROXY_RES
            );
        }).rejects.toThrow();
    });
});

describe('createCipherMiddleware', () => {
    const createProxy = (...params) => { return { ...params }; };
    const getStrategy = () => { return 'getStrategy'; };

    test('defined as expected', () => {
        const proxy = createCipherMiddleware({
            createProxy,
            getStrategy,
            LOGGER,
            HOST
        });

        expect(proxy).toBeDefined();
    });

    test('props as default value', () => {
        expect(() => {
            createCipherMiddleware();
        }).toThrow();
    });
});

describe('createProxy', () => {
    const createProxy = (host, options) => {
        return options;
    };

    const proxy = createCipherMiddleware({ createProxy, getStrategy: GET_STRATEGY, logger: LOGGER, host: HOST });

    describe('userReqBodyDecorator', () => {
        test('test in proxy function', async () => {
            const result = await proxy.proxyReqBodyDecorator({}, { method: 'POST', originalUrl: '/v1/tasks/take' });

            expect(result).toBeDefined();
        });
    });

    describe('userResDecorator', () => {
        test('test in proxy function', async () => {
            const result = await proxy.userResDecorator({}, {}, { method: 'POST', originalUrl: '/v1/tasks/take' }, {});

            expect(result).toBeDefined();
        });
    });

    describe('errorHandler', () => {
        const STRATEGY_ERROR = new StrategyError();
        const OTHER_ERROR = new Error();
        const ORIGINAL_URL = '/me';
        const ERROR_MESSAGE = 'Internal error';
        const VALID_RES = {
            req: { originalUrl: ORIGINAL_URL },
            statusCode: 200,
            status(code) {
                this.statusCode = code;
                return this;
            },
            json(message) {
                this.message = message;
                return this;
            }
        };

        const RES_WITHOUT_REQ = {
            statusCode: 200,
            status(code) {
                this.statusCode = code;
                return this;
            },
            json(message) {
                this.message = message;
                return this;
            }
        };

        test('with StrategyError', () => {
            const { req: { originalUrl }, statusCode, message: { error } } = proxy.proxyErrorHandler(STRATEGY_ERROR, VALID_RES);

            expect(originalUrl).toBe(ORIGINAL_URL);
            expect(error).toBe(ERROR_MESSAGE);
            expect(statusCode).toBe(400);
        });

        test('with other error', () => {
            const { req: { originalUrl }, statusCode, message: { error } } = proxy.proxyErrorHandler(OTHER_ERROR, VALID_RES);

            expect(originalUrl).toBe(ORIGINAL_URL);
            expect(error).toBe(ERROR_MESSAGE);
            expect(statusCode).toBe(500);
        });

        test('without empty res.req', () => {
            const { req } = proxy.proxyErrorHandler(OTHER_ERROR, RES_WITHOUT_REQ);

            expect(req).toBeUndefined();
        });

        test('with empty res', () => {
            const err = new Error();

            expect(() => {
                proxy.proxyErrorHandler(err);
            }).toThrow();
        });
    });
});
