import {Task} from 'redux-saga';
import {expectSaga} from 'redux-saga-test-plan';
import {all, call, delay, fork} from 'redux-saga/effects';

import {cache} from '../utils';

describe('cache', () => {
    const RESULT = {items: ['']};

    const requestAsync = jest.fn((delay?: number, result?: any) => {
        return new Promise(resolve => {
            if (delay) {
                setTimeout(() => resolve(result || RESULT), delay);
                return;
            }

            resolve(result || RESULT);
        });
    });

    const requestSync = jest.fn(() => {
        return RESULT;
    });

    const requestGen = jest.fn(function * () {
        yield delay(50);
        return RESULT;
    });

    beforeEach(() => {
        requestAsync.mockClear();
        requestSync.mockClear();
        requestGen.mockClear();
    });

    test('cached sync function called once in parallel', () => {
        const cachedFn = jest.fn(cache(requestSync));
        let result: any;

        return expectSaga(function* () {
            result = yield all([
                call(cachedFn),
                call(cachedFn),
                call(cachedFn)
            ]);
        })
            .run()
            .then(() => {
                expect(cachedFn).toHaveBeenCalledTimes(3);
                expect(requestSync).toHaveBeenCalledTimes(1);
                expect(result).toEqual([RESULT, RESULT, RESULT]);
            });

    });

    test('cached async function called once in parallel', () => {
        const cachedFn = jest.fn(cache(requestAsync));
        let result: any;

        return expectSaga(function* () {
            result = yield all([
                call(cachedFn, 50),
                call(cachedFn, 50),
                call(cachedFn, 50)
            ]);
        })
            .run()
            .then(() => {
                expect(cachedFn).toHaveBeenCalledTimes(3);
                expect(requestAsync).toHaveBeenCalledTimes(1);
                expect(requestAsync).toHaveBeenCalledWith(50);
                expect(result).toEqual([RESULT, RESULT, RESULT]);
            });

    });

    test('cached gen function called once in parallel', () => {
        const cachedFn = jest.fn(cache(requestGen));
        let result: any;

        return expectSaga(function* () {
            result = yield all([
                call(cachedFn),
                call(cachedFn),
                call(cachedFn)
            ]);
        })
            .run()
            .then(() => {
                expect(cachedFn).toHaveBeenCalledTimes(3);
                expect(requestGen).toHaveBeenCalledTimes(1);
                expect(result).toEqual([RESULT, RESULT, RESULT]);
            });

    });

    test('cached function called once sequentially', () => {
        const cachedFn = jest.fn(cache(requestAsync));
        const result: any[] = [];

        return expectSaga(function* () {
            result.push(yield call(cachedFn, 50));
            result.push(yield call(cachedFn, 50));
            result.push(yield call(cachedFn, 50));
        })
            .run()
            .then(() => {
                expect(cachedFn).toHaveBeenCalledTimes(3);
                expect(requestAsync).toHaveBeenCalledTimes(1);
                expect(requestAsync).toHaveBeenCalledWith(50);
                expect(result).toEqual([RESULT, RESULT, RESULT]);
            });

    });

    test('cached function reset', () => {
        const cachedFn = cache(requestAsync);
        const result: any[] = [];

        return expectSaga(function* () {
            result.push(yield call(cachedFn, 50));
            result.push(yield call(cachedFn, 50));

            cachedFn.resetCache();
            result.push(yield call(cachedFn, 50));
        })
            .run()
            .then(() => {
                expect(requestAsync).toHaveBeenCalledTimes(2);
                expect(requestAsync).toHaveBeenCalledWith(50);
                expect(result).toEqual([RESULT, RESULT, RESULT]);
            });

    });

    test('cached function expired', () => {
        const expiration = 50;
        const cachedFn = cache(requestAsync, {expire: expiration});
        const result: any[] = [];

        return expectSaga(function* () {
            result.push(...(yield all([
                call(cachedFn, 5, 'xxx'),
                call(cachedFn, 5, 'xxx'),
                call(cachedFn, 5, 'xxx1')
            ])));

            yield delay(expiration);

            result.push(yield call(cachedFn, 1, 'yyy'));
            result.push(yield call(cachedFn, 1, 'yyy'));
            result.push(yield call(cachedFn, 1, 'yyy1'));

            yield delay(expiration);

            result.push(...(yield all([
                call(cachedFn, 10, 'zzz'),
                call(cachedFn, 10, 'zzz'),
                call(cachedFn, 10, 'zzz1')
            ])));
        })
            .run()
            .then(() => {
                expect(requestAsync).toHaveBeenCalledTimes(6);
                expect(requestAsync).toHaveBeenNthCalledWith(1, 5, 'xxx');
                expect(requestAsync).toHaveBeenNthCalledWith(2, 5, 'xxx1');
                expect(requestAsync).toHaveBeenNthCalledWith(3, 1, 'yyy');
                expect(requestAsync).toHaveBeenNthCalledWith(4, 1, 'yyy1');
                expect(requestAsync).toHaveBeenNthCalledWith(5, 10, 'zzz');
                expect(requestAsync).toHaveBeenNthCalledWith(6, 10, 'zzz1');
                expect(result).toEqual(['xxx', 'xxx', 'xxx1', 'yyy', 'yyy', 'yyy1', 'zzz', 'zzz', 'zzz1']);
            });

    });

    test('cached function canceled before respond', () => {
        const cachedFn = cache(requestAsync);
        const result: any[] = [];

        return expectSaga(function* () {
            const task: Task = yield fork(function * () {
                yield call(cachedFn, 100);
            });

            yield delay(10);
            task.cancel();

            result.push(yield call(cachedFn, 1, 'yyy'));
        })
            .run()
            .then(() => {
                expect(requestAsync).toHaveBeenCalledTimes(2);
                expect(requestAsync).toHaveBeenNthCalledWith(2, 1, 'yyy');
                expect(result).toEqual(['yyy']);
            });

    });
});
