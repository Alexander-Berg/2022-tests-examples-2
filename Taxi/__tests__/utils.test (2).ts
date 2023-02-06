import {all, call, delay} from 'typed-redux-saga';

import {getSagaRunner} from '../helpers';
import {batch} from '../utils';

const DELAY = 10;

test('batch serial call', () => {
    const m = jest.fn();

    const batchedFoo = batch(function* foo(...args: any[]) {
        m(...args);
        yield* delay(DELAY);
    });

    return getSagaRunner()
        .run(function* () {
            yield* call(batchedFoo, 1);
            yield* call(batchedFoo, 1);

            expect(m).toHaveBeenCalledTimes(2);
            expect(m).toHaveBeenNthCalledWith(1, 1);
            expect(m).toHaveBeenNthCalledWith(2, 1);
        })
        .toPromise();
});

test('batch parallel call with same args', () => {
    const m = jest.fn();

    const batchedFoo = batch(function* foo(...args: any[]) {
        m(...args);
        yield* delay(DELAY);
        return args;
    });

    return getSagaRunner()
        .run(function* () {
            const [res1, res2] = yield* all([call(batchedFoo, 1), call(batchedFoo, 1)]);

            expect(m).toHaveBeenCalledTimes(1);
            expect(m).toHaveBeenNthCalledWith(1, 1);
            expect(res1).toBe(res2);
        })
        .toPromise();
});

test('batch parallel call with different args', () => {
    const m = jest.fn();

    const batchedFoo = batch(function* foo(...args: any[]) {
        m(...args);
        yield* delay(DELAY);
        return args;
    });

    return getSagaRunner()
        .run(function* () {
            const [res1, res2] = yield* all([call(batchedFoo, 1), call(batchedFoo, 2)]);

            expect(m).toHaveBeenCalledTimes(2);
            expect(m).toHaveBeenNthCalledWith(1, 1);
            expect(m).toHaveBeenNthCalledWith(2, 2);
            expect(res1).toEqual([1]);
            expect(res2).toEqual([2]);
        })
        .toPromise();
});

test('batch parallel call with same func same args', () => {
    const batchedFoo = batch(function* foo(cb: (...args: any[]) => any, ...rest: any[]) {
        // eslint-disable-next-line standard/no-callback-literal
        const res = cb(...rest);
        yield* delay(DELAY);
        return res;
    });

    const sum = jest.fn((x: number) => x + x);

    return getSagaRunner()
        .run(function* () {
            const [res1, res2] = yield* all([call(batchedFoo, sum, 1), call(batchedFoo, sum, 1)]);

            expect(sum).toHaveBeenCalledTimes(1);
            expect(res1).toBe(res2);
        })
        .toPromise();
});

test('batch parallel call with same func different args', () => {
    const batchedFoo = batch(function* foo(cb: (...args: any[]) => any, ...rest: any[]) {
        // eslint-disable-next-line standard/no-callback-literal
        const res = cb(...rest);
        yield* delay(DELAY);
        return res;
    });

    const sum = jest.fn((x: number) => x + x);

    return getSagaRunner()
        .run(function* () {
            const [res1, res2] = yield* all([call(batchedFoo, sum, 1), call(batchedFoo, sum, 2)]);

            expect(sum).toHaveBeenCalledTimes(2);
            expect(res1).toBe(2);
            expect(res2).toBe(4);
        })
        .toPromise();
});

test('batch parallel call with different funcs', () => {
    const batchedFoo = batch(function* foo(cb: (...args: any[]) => any, ...rest: any[]) {
        // eslint-disable-next-line standard/no-callback-literal
        const res = cb(...rest);
        yield* delay(DELAY);
        return res;
    });

    const sum = jest.fn((x: number) => x + x);
    const multi = jest.fn((x: number) => x * x);

    return getSagaRunner()
        .run(function* () {
            const [res1, res2] = yield* all([call(batchedFoo, sum, 1), call(batchedFoo, multi, 2)]);

            expect(sum).toHaveBeenCalledTimes(1);
            expect(multi).toHaveBeenCalledTimes(1);

            expect(res1).toEqual(2);
            expect(res2).toEqual(4);
        })
        .toPromise();
});
