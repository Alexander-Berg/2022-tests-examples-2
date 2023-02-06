import {expectSaga} from 'redux-saga-test-plan';
import {call} from 'typed-redux-saga';

import {BaseHttpAPI} from '_pkg/isomorphic/api';
import {mockRequest} from '_pkg/isomorphic/utils/mockRequest';

import {pollRequest} from '../pollRequest';

const TEST_URL = '/test/';

class TestAPI extends BaseHttpAPI {
    public test = () => {
        return this.post(TEST_URL);
    }

    public testWithError = () => {
        throw new Error();
    }
}

const api = new TestAPI({
    baseURL: ''
});

window.XMLHttpRequest = mockRequest;

describe('pollRequest', () => {
    describe('should work', () => {
        const defaultSaga = (func: any) => function * () {
            const request = func;
            return yield* call(request);
        };

        beforeEach(() => {
            mockRequest.clear();
        });

        test('with simple 200', () => {
            mockRequest.addMock('post', TEST_URL)
                .addResponse({status: 'pending'}, 200)
                .addResponse({status: 'pending'}, 200)
                .addResponse({status: 'completed'}, 200);

            const polling = pollRequest(api.test, {delay: 10});
            const func = jest.fn(polling);

            return expectSaga(defaultSaga(func))
                .run({timeout: 500})
                .then(data => {
                    expect(data.returnValue.status).toBe('completed');
                });
        });

        test('with param completeCondition', () => {
            mockRequest.addMock('post', TEST_URL)
                .addResponse({status: 'pending'}, 200)
                .addResponse({status: 'anything'}, 200)
                .addResponse({status: 'pending'}, 200)
                .addResponse({status: 'completed'}, 200)
                .addResponse({status: 'pending'}, 200)
                .addResponse({status: 'test'}, 200)
                .addResponse({status: 'someCustomStatus'}, 200);

            const polling = pollRequest(api.test,
                {
                    delay: 10,
                    completeCondition: (res: any) => ['someCustomStatus'].includes(res.status)
            });
            const func = jest.fn(polling);

            return expectSaga(defaultSaga(func))
                .run({timeout: 500})
                .then(data => {
                    expect(data.returnValue.status).toBe('someCustomStatus');
                });
        });

        test('with script error', () => {
            const polling = pollRequest(api.testWithError, {delay: 10});
            const func = jest.fn(polling);

            return expectSaga(defaultSaga(func))
                .run({timeout: 500})
                .catch(err => {
                    expect(err).toBeInstanceOf(Error);
                });
        });

    });
});
