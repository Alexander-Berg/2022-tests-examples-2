import {expectSaga} from 'redux-saga-test-plan';
import {call} from 'redux-saga/effects';

import {BaseHttpAPI} from '_pkg/isomorphic/api';
import {mockRequest} from '_pkg/isomorphic/utils/mockRequest';

import {idempotent} from '../idempotent';
import {RETRY_DEFAULTS} from '../retry';

const TEST_URL = '/test/';

class TestAPI extends BaseHttpAPI {
    public test = (params: {$idempotencyToken: string}) => {
        return this.get(TEST_URL, null, {
            timeout: RETRY_DEFAULTS.delay
        });
    }

    public testWithError = (params: {$idempotencyToken: string}) => {
        throw new Error();
    }
}

const api = new TestAPI({
    baseURL: ''
});

window.XMLHttpRequest = mockRequest;

describe('idempotent', () => {
    describe('non empty object', () => {
        const defaultSaga = (func: (params: {$idempotencyToken: string}) => unknown) => function * () {
            const request = idempotent(func);

            try {
                yield call(request, {x: 1});
            } catch {
                // ignore
            }

            yield call(request, {x: 1});
        };

        beforeEach(() => {
            mockRequest.clear();
        });

        test('args passed', () => {
            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 200)
                .addResponse({}, 200);

            const func = jest.fn(api.test);

            return expectSaga(defaultSaga(func))
                .run()
                .then(() => {
                    expect(func).toHaveBeenCalledTimes(2);
                    expect((func.mock.calls[1][0] as any).x).toBe(1);
                    expect(func.mock.calls[1][0].$idempotencyToken).toBeTruthy();
                });
        });

        test('timeout', () => {
            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 200, RETRY_DEFAULTS.delay * 2)
                .addResponse({}, 200);

            const func = jest.fn(api.test);

            return expectSaga(defaultSaga(func))
                .run({timeout: RETRY_DEFAULTS.delay * 10})
                .then(() => {
                    expect(func).toHaveBeenCalledTimes(2);
                    expect(func.mock.calls[0][0].$idempotencyToken).toBe(func.mock.calls[1][0].$idempotencyToken);
                });
        });

        test('500', () => {
            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 500)
                .addResponse({}, 200);

            const func = jest.fn(api.test);

            return expectSaga(defaultSaga(func))
                .run({timeout: RETRY_DEFAULTS.delay * 10})
                .then(() => {
                    expect(func).toHaveBeenCalledTimes(2);
                    expect(func.mock.calls[0][0].$idempotencyToken).toBe(func.mock.calls[1][0].$idempotencyToken);
                });
        });

        test('script errors', () => {
            const func = jest.fn(api.testWithError);

            return expectSaga(defaultSaga(func))
                .run({timeout: RETRY_DEFAULTS.delay * 10})
                .then(() => {
                    throw new Error('Unexpected behavior');
                }, () => {
                    expect(func).toHaveBeenCalledTimes(2);
                    expect(func.mock.calls[0][0].$idempotencyToken).not.toBe(func.mock.calls[1][0].$idempotencyToken);
                });
        });

        test('non 500', () => {
            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 400)
                .addResponse({}, 200);

            const func = jest.fn(api.test);

            return expectSaga(defaultSaga(func))
                .run({timeout: RETRY_DEFAULTS.delay * 10})
                .then(() => {
                    expect(func).toHaveBeenCalledTimes(2);
                    expect(func.mock.calls[0][0].$idempotencyToken).not.toBe(func.mock.calls[1][0].$idempotencyToken);
                });
        });

        test('test token if keys has different sort', () => {
            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 200, RETRY_DEFAULTS.delay * 2)
                .addResponse({}, 200);

            const func = jest.fn(api.test);

            return expectSaga(function * () {
                const request = idempotent(func);

                try {
                    yield call(request, {
                        x: 1,
                        y: {
                            a: 2,
                            b: [{
                                z: 1,
                                x: 2
                            }]
                        }
                    });
                } catch {
                    // ignore
                }

                yield call(request, {
                    y: {
                        b: [{
                            x: 2,
                            z: 1
                        }],
                        a: 2
                    },
                    x: 1
                });
            })
                .run({timeout: RETRY_DEFAULTS.delay * 10})
                .then(() => {
                    expect(func).toHaveBeenCalledTimes(2);
                    expect(func.mock.calls[0][0].$idempotencyToken).toBe(func.mock.calls[1][0].$idempotencyToken);
                });
        });

        test('test token if params changed', () => {
            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 200, RETRY_DEFAULTS.delay * 2)
                .addResponse({}, 200);

            const func = jest.fn(api.test);

            return expectSaga(function * () {
                const request = idempotent(func);

                try {
                    yield call(request, {y: {b: [{z: 1, x: 2}]}});
                } catch {
                    // ignore
                }

                yield call(request, {y: {b: [{x: '2', z: 1}]}});
            })
                .run({timeout: RETRY_DEFAULTS.delay * 10})
                .then(() => {
                    expect(func).toHaveBeenCalledTimes(2);
                    expect(func.mock.calls[0][0].$idempotencyToken).not.toBe(func.mock.calls[1][0].$idempotencyToken);
                });
        });

        test('repeat request with other request in between', () => {
            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 200, RETRY_DEFAULTS.delay * 2)
                .addResponse({}, 200)
                .addResponse({}, 200);

            const func = jest.fn(api.test);

            return expectSaga(function * () {
                const request = idempotent(func);

                try {
                    yield call(request, {y: {b: [{z: 1, x: 2}]}});
                } catch {
                    // ignore
                }

                yield call(request, {y: {b: [{x: '2', z: 1}]}});
                yield call(request, {y: {b: [{z: 1, x: 2}]}});
            })
                .run({timeout: RETRY_DEFAULTS.delay * 10})
                .then(() => {
                    expect(func).toHaveBeenCalledTimes(3);
                    expect(func.mock.calls[0][0].$idempotencyToken).toBe(func.mock.calls[2][0].$idempotencyToken);
                });
        });
    });

    describe('empty object', () => {
        const defaultSaga = (func: (params: {$idempotencyToken: string}) => unknown) => function * () {
            const request = idempotent(func);
            yield call(request, {});
        };

        beforeEach(() => {
            mockRequest.clear();
        });

        test('args passed', () => {
            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 200);

            const func = jest.fn(api.test);

            return expectSaga(defaultSaga(func))
                .run()
                .then(() => {
                    expect(func).toHaveBeenCalledTimes(1);
                    expect(func.mock.calls[0][0].$idempotencyToken).toBeTruthy();
                });
        });

        test('timeout', () => {
            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 200, RETRY_DEFAULTS.delay * 2)
                .addResponse({}, 200);

            const func = jest.fn(api.test);

            return expectSaga(defaultSaga(func))
                .run({timeout: RETRY_DEFAULTS.delay * 10})
                .then(() => {
                    expect(func).toHaveBeenCalledTimes(2);
                    expect(func.mock.calls[0][0].$idempotencyToken).toBe(func.mock.calls[1][0].$idempotencyToken);
                });
        });

        test('500', () => {
            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 500)
                .addResponse({}, 200);

            const func = jest.fn(api.test);

            return expectSaga(defaultSaga(func))
                .run({timeout: RETRY_DEFAULTS.delay * 10})
                .then(() => {
                    expect(func).toHaveBeenCalledTimes(2);
                    expect(func.mock.calls[0][0].$idempotencyToken).toBe(func.mock.calls[1][0].$idempotencyToken);
                });
        });

        test('script errors', () => {
            const func = jest.fn(api.testWithError);

            return expectSaga(function * () {
                try {
                    yield call(defaultSaga(func));
                } catch {
                    // ignore
                }

                yield call(defaultSaga(func));
            })
                .run({timeout: RETRY_DEFAULTS.delay * 10})
                .then(() => {
                    throw new Error('Unexpected behavior');
                }, () => {
                    expect(func).toHaveBeenCalledTimes(2);
                    expect(func.mock.calls[0][0].$idempotencyToken).not.toBe(func.mock.calls[1][0].$idempotencyToken);
                });
        });

        test('non 500', () => {
            mockRequest.addMock('get', TEST_URL)
                .addResponse({}, 400)
                .addResponse({}, 200);

            const func = jest.fn(api.test);

            return expectSaga(function * () {
                try {
                    yield call(defaultSaga(func));
                } catch {
                    // ignore

                }
                yield call(defaultSaga(func));
            })
                .run({timeout: RETRY_DEFAULTS.delay * 10})
                .then(() => {
                    expect(func).toHaveBeenCalledTimes(2);
                    expect(func.mock.calls[0][0].$idempotencyToken).not.toBe(func.mock.calls[1][0].$idempotencyToken);
                });
        });
    });
});
