import { Server } from 'http';
import { URLSearchParams } from 'url';

import { Request } from 'express';
import got from 'got';

import { getServer, runServer } from 'server/utils';

import { simpleRequestWrapper } from '..';
import {
    omitSearchParams,
    toCamelCase,
    toSnakeCaseBody,
    ulogin,
} from '../hooks';
import {
    addQueryParam,
    setQueryParam,
    setQueryParamFromContext,
} from '../utils';

describe('request', () => {
    describe('simpleRequestWrapper', () => {
        let mockServerUrl = '';
        let mockServer: Server;
        beforeEach(async () => {
            return runServer(getServer()).then((incomingMockServer) => {
                mockServer = incomingMockServer.server;
                mockServerUrl = incomingMockServer.url;
            });
        });
        afterEach(async () => {
            return Promise.all([
                // todo promisify почему то не работает
                new Promise((resolve) => {
                    mockServer.close(resolve);
                }),
            ]);
        });

        // todo по какой-то причине нельзя сравнить два promise через ===
        // возможно из-за https://github.com/sindresorhus/p-cancelable/issues/21
        // поэтому приходится проверять напрямую cacheHttpAdapter
        it('caches get request', () => {
            const wrapper = simpleRequestWrapper(got);
            const context = ({
                cacheHttpAdapter: new Map(),
            } as unknown) as Request;
            const options = {
                context,
                searchParams: {
                    a: 1,
                },
            };
            const url = `${mockServerUrl}/success/caches`;

            wrapper.get(url, options);
            expect(context.cacheHttpAdapter?.size).toBe(1);
            wrapper.get(url, options);
            expect(context.cacheHttpAdapter?.size).toBe(1);
        });

        it(`doesn't cache urls with different get params`, () => {
            const wrapper = simpleRequestWrapper(got);
            const context = ({
                cacheHttpAdapter: new Map(),
            } as unknown) as Request;
            const options = {
                context,
                searchParams: {
                    a: 1,
                },
            };
            const url = `${mockServerUrl}/success/caches`;

            wrapper.get(url, {
                ...options,
                searchParams: {
                    a: 1,
                },
            });
            expect(context.cacheHttpAdapter?.size).toBe(1);
            wrapper.get(url, {
                ...options,
                searchParams: {
                    a: 2,
                },
            });
            expect(context.cacheHttpAdapter?.size).toBe(2);
        });

        it(`doesn't cache non GET requests`, async () => {
            const wrapper = simpleRequestWrapper(got);
            const context = ({
                cacheHttpAdapter: new Map(),
            } as unknown) as Request;
            const options = {
                context,
            };
            const url = `${mockServerUrl}/success/caches`;

            await wrapper.post(url, options);
            await wrapper.put(url, options);

            expect(context.cacheHttpAdapter?.size).toBe(0);
        });

        it(`doesn't fail without cacheHttpAdapter`, () => {
            const wrapper = simpleRequestWrapper(got);

            const promise1 = wrapper.get(`${mockServerUrl}/success`);
            const promise2 = wrapper.get(`${mockServerUrl}/success`);

            expect(promise1 === promise2).toBe(false);
        });
    });

    describe('utils', () => {
        describe('addQueryParam', () => {
            it('works with plain object', () => {
                const searchParams = {};

                addQueryParam(searchParams, 'a', '1');

                expect(searchParams).toEqual({ a: '1' });
            });

            it('works with URLSearchParams', () => {
                const searchParams = new URLSearchParams();

                addQueryParam(searchParams, 'a', '1');

                expect(searchParams.toString()).toEqual('a=1');
            });
        });

        describe('setQueryParam', () => {
            it('works', () => {
                const setValue = setQueryParam('key', 'value');
                const options = {
                    searchParams: {},
                };

                setValue(options);

                expect(options.searchParams).toEqual({
                    key: 'value',
                });
            });
        });

        describe('setQueryParamFromContext', () => {
            it('works with simple value', () => {
                const setValue = setQueryParamFromContext(
                    'keyInQuery',
                    'pathFromContext',
                );
                const options = {
                    searchParams: {},
                    context: {
                        pathFromContext: 1,
                    },
                };

                setValue(options);

                expect(options.searchParams).toEqual({
                    keyInQuery: 1,
                });
            });

            it('works with composite path', () => {
                const setValue = setQueryParamFromContext(
                    'keyInQuery',
                    'path.from.context',
                );
                const options = {
                    searchParams: {},
                    context: {
                        path: {
                            from: {
                                context: 1,
                            },
                        },
                    },
                };

                setValue(options);

                expect(options.searchParams).toEqual({
                    keyInQuery: 1,
                });
            });

            it('works with URLSearchParams', () => {
                const setValue = setQueryParamFromContext(
                    'keyInQuery',
                    'pathFromContext',
                );
                const options = {
                    searchParams: new URLSearchParams(),
                    context: {
                        pathFromContext: 1,
                    },
                };

                setValue(options);

                expect(options.searchParams.toString()).toEqual('keyInQuery=1');
            });

            it(`doesn't fail with missed query`, () => {
                const setValue = setQueryParamFromContext(
                    'keyInQuery',
                    'pathFromContext',
                );
                const options = {
                    context: {
                        pathFromContext: 1,
                    },
                };

                expect(() => {
                    setValue(options);
                }).not.toThrow();
            });
        });
    });

    describe('hooks', () => {
        let mockServerUrl = '';
        let mockServer: Server;
        beforeEach(async () => {
            return runServer(getServer()).then((incomingMockServer) => {
                mockServer = incomingMockServer.server;
                mockServerUrl = incomingMockServer.url;
            });
        });

        afterEach(async () => {
            return Promise.all([
                // todo promisify почему то не работает
                new Promise((resolve) => {
                    mockServer.close(resolve);
                }),
            ]);
        });

        describe('toSnakeCaseBody', () => {
            it('works', async () => {
                const { body } = await got.post(`${mockServerUrl}/json-body`, {
                    json: { futureSnakeCase: 1 },
                    responseType: 'json',
                    hooks: {
                        init: [toSnakeCaseBody],
                    },
                });

                /* eslint-disable camelcase */
                expect(body).toEqual({
                    future_snake_case: 1,
                });
                /* eslint-enable camelcase */
            });
        });

        describe('toCamelCase', () => {
            it('works', async () => {
                const { body } = await got.post(`${mockServerUrl}/json-body`, {
                    // eslint-disable-next-line camelcase
                    json: { future_camel_case: 1 },
                    responseType: 'json',
                    hooks: {
                        afterResponse: [toCamelCase],
                    },
                });

                expect(body).toEqual({ futureCamelCase: 1 });
            });
        });

        describe('omitSearchParams', () => {
            it('works', async () => {
                const instance = got.extend({
                    hooks: {
                        init: [omitSearchParams],
                        beforeRequest: [
                            ({ searchParams }) => {
                                expect(searchParams?.toString()).toEqual(
                                    'shouldStay=1',
                                );
                            },
                        ],
                    },
                });
                const wrapper = simpleRequestWrapper(instance);

                await wrapper.get(`${mockServerUrl}/success`, {
                    searchParams: {
                        ulogin: null,
                        shouldStay: 1,
                    },
                });
            });
        });

        describe('omit ulogin', () => {
            it('no send ulogin with null', async () => {
                const instance = got.extend({
                    hooks: {
                        init: [ulogin, omitSearchParams],
                        beforeRequest: [
                            ({ searchParams }) => {
                                expect(searchParams?.toString()).toEqual(
                                    'shouldStay=1',
                                );
                            },
                        ],
                    },
                });

                const wrapper = simpleRequestWrapper(instance);
                await wrapper.get(`${mockServerUrl}/success`, {
                    searchParams: {
                        ulogin: null,
                        shouldStay: 1,
                    },
                    context: ({
                        query: {
                            ulogin: 'test',
                        },
                    } as unknown) as Request,
                });
            });

            it('send searchParams ulogin', async () => {
                const instance = got.extend({
                    hooks: {
                        init: [ulogin, omitSearchParams],
                        beforeRequest: [
                            ({ searchParams }) => {
                                expect(searchParams?.toString()).toEqual(
                                    'ulogin=searchParamsUlogin&shouldStay=1',
                                );
                            },
                        ],
                    },
                });

                const wrapper = simpleRequestWrapper(instance);
                await wrapper.get(`${mockServerUrl}/success`, {
                    searchParams: {
                        ulogin: 'searchParamsUlogin',
                        shouldStay: 1,
                    },
                    context: ({
                        query: {
                            ulogin: 'test',
                        },
                    } as unknown) as Request,
                });
            });

            it('send query ulogin', async () => {
                const instance = got.extend({
                    hooks: {
                        init: [ulogin, omitSearchParams],
                        beforeRequest: [
                            ({ searchParams }) => {
                                expect(searchParams?.toString()).toEqual(
                                    'shouldStay=1&ulogin=queryUlogin',
                                );
                            },
                        ],
                    },
                });
                const queryUlogin = 'queryUlogin';
                const options = {
                    searchParams: {
                        shouldStay: 1,
                    },
                    context: ({
                        query: {
                            ulogin: queryUlogin,
                        },
                    } as unknown) as Request,
                };
                const wrapper = simpleRequestWrapper(instance);
                await wrapper.get(`${mockServerUrl}/success`, options);
            });
        });
    });
});
