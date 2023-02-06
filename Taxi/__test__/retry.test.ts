import {expectSaga} from 'redux-saga-test-plan';
import {call} from 'redux-saga/effects';

import {retry, RETRY_DEFAULTS} from '../retry';

describe('retry', () => {
    test('test defaults', () => {
        const func = jest.fn(() => {
            throw new Error();
        });

        const start = Date.now();
        const retries = Number(RETRY_DEFAULTS.retries);

        return expectSaga(retry(func))
            .run({timeout: RETRY_DEFAULTS.delay * 10})
            .then(() => {
                throw new Error('Unexpected behavior');
            }, () => {
                expect(func).toBeCalledTimes(retries + 1);
                expect(Date.now() - start).toBeGreaterThan(RETRY_DEFAULTS.delay * retries);
            });
    });

    test('args passed', () => {
        const func = jest.fn((...args: number[]) => null);

        return expectSaga(function * () {
            yield call(retry(func), 1, 2, 3);
        })
            .run({timeout: RETRY_DEFAULTS.delay * 10})
            .then(() => {
                expect(func).toHaveBeenCalledWith(1, 2, 3);
            });
    });

    test('custom options', () => {
        const func = jest.fn(() => {
            throw new Error();
        });

        let maxRetries = 4;
        const expectedCalls = maxRetries + 1;
        const retries = jest.fn(() => {
            return (maxRetries-- > 0);
        });

        return expectSaga(retry(func, {
            retries,
            delay: 0
        }))
            .run({timeout: RETRY_DEFAULTS.delay * 10})
            .then(() => {
                throw new Error('Unexpected behavior');
            }, () => {
                expect(func).toBeCalledTimes(expectedCalls);
                expect(retries).toBeCalledTimes(expectedCalls);
            });
    });
});
