import {OperationService, Service} from '@iiiristram/sagun';

import {all, call, delay} from 'typed-redux-saga';

import {batch} from '../decorators/batch';
import {getSagaRunner} from '../helpers';

const operationService = new OperationService({hash: {}});

const DELAY = 10;

test('batch decorator', () => {
    const m = jest.fn();

    class TestService extends Service {
        toString() {
            return 'TestService';
        }

        @batch
        *foo(...args: any[]) {
            expect(this instanceof TestService).toBeTruthy();
            m(...args);
            yield* delay(DELAY);
            return args;
        }
    }

    const testService = new TestService(operationService);
    const {run} = getSagaRunner();

    return run(function* () {
        const [res1, res2] = yield* all([call(testService.foo, 1), call(testService.foo, 1)]);

        expect(m).toHaveBeenCalledTimes(1);
        expect(m).toHaveBeenNthCalledWith(1, 1);
        expect(res1).toBe(res2);

        const [res3, res4] = yield* all([call(testService.foo, 2), call(testService.foo, 3)]);

        expect(m).toHaveBeenCalledTimes(3);
        expect(m).toHaveBeenNthCalledWith(2, 2);
        expect(m).toHaveBeenNthCalledWith(3, 3);
        expect(res3).toEqual([2]);
        expect(res4).toEqual([3]);
    }).toPromise();
});
