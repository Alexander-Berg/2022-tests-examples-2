import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';
import {throwError} from 'redux-saga-test-plan/providers';
import {delay} from 'redux-saga/effects';

import reducer from '_pkg/reducers/asyncOperations';
import ErrorModalService from '_pkg/sagas/services/ErrorModalService';

import {AsyncOperation} from '_types/common/infrastructure';
import {createDaemon} from '../createDaemon';
import {DaemonMode, daemonRunner, errorHandler, operationRunner} from '../utils';

const originalLog = console.error;

describe('sagas utils', () => {
    beforeAll(() => {
        console.error = jest.fn(() => {/*  */});
    });

    afterAll(() => {
        console.error = originalLog;
    });

    describe('errorHandler', () => {
        test('Проверяем что переданная функция вызывается с верными аргументами', () => {
            let result = 0;
            const sum = function * (a: number, b: number) {
                result += a + b;
                return result;
            };

            return expectSaga(errorHandler(sum), 1, 1)
                .run()
                .then(() => {
                    expect(result).toBe(2);
                });
        });

        test('Проверяем вызов модалки при ошибке', () => {
            const func = () => { /* */ };
            const error = new Error('Exception');

            return expectSaga(errorHandler(func))
                .provide([
                    [matchers.call.fn(func), throwError(error)]
                ])
                .call(ErrorModalService.add, error)
                .run();
        });

        test('Проверяем что ошибка может всплывать', () => {
            const func = () => { /* */ };
            const error = new Error('Exception');
            const onErrorHandled = () => Promise.reject(new Error('Exceptions do not bubble'));
            const onErrorBubble = () => Promise.resolve();

            return expectSaga(errorHandler(func, true))
                .provide([
                    [matchers.call.fn(func), throwError(error)]
                ])
                .run()
                .then(onErrorHandled, onErrorBubble);
        });
    });

    describe('operationRunner', () => {
        test('Проверяем что переданная функция вызывается с верными аргументами', () => {
            let result = 0;
            const sum = function * (a: number, b: number) {
                result += a + b;
                return result;
            };
            const operation = operationRunner('id', sum);

            return expectSaga(operation.run, 1, 1)
                .run()
                .then(() => {
                    expect(result).toBe(2);
                });
        });

        test('Проверяем что ошибки всплывают', () => {
            function * func() { /* */ }
            const error = new Error('Exception');
            const operation = operationRunner('id', func);
            const onErrorHandled = () => Promise.reject(new Error('Exceptions do not bubble'));
            const onErrorBubble = () => Promise.resolve();

            return expectSaga(operation.run)
                .provide([
                    [matchers.call.fn(func), throwError(error)]
                ])
                .run()
                .then(onErrorHandled, onErrorBubble);
        });

        test('Проверяем что операция создается в сторе', () => {
            const id = 'id';
            function * func() { /* */ }
            const operation = operationRunner(id, func);

            return expectSaga(operation.run)
                .withReducer(reducer)
                .run()
                .then(result => {
                    expect(result.storeState).toMatchObject({
                        [id]: {isLoading: false, args: []}
                    });
                });
        });

        test('Проверяем что операция создается даже в случае ошибки', () => {
            const id = 'id';
            function * func() { /* */ }
            const error = new Error('Exception');
            const operation = operationRunner(id, func);

            // приходится экранировать ошибку через errorHandler
            // иначе не получится получить стор из результата
            return expectSaga(errorHandler(operation.run))
                .withReducer(reducer)
                .provide([
                    [matchers.call.fn(func), throwError(error)]
                ])
                .run()
                .then(result => {
                    expect(result.storeState).toMatchObject({
                        [id]: {isLoading: false, isError: true, error}
                    });
                });
        });

        test('Проверяем удаление операции', () => {
            const id = 'id';
            function * func() { /* */ }
            const operation = operationRunner(id, func);

            return expectSaga(operation.destroy)
                .withReducer(reducer)
                .withState({
                    [id]: {isLoading: false}
                })
                .run()
                .then(result => {
                    expect(result.storeState).not.toHaveProperty(id);
                });
        });

        test('Проверяем что операция со стратгией возвращает результат вызова функции', () => {
            const id = 'id';
            const func = function * () {
                return 1;
             };

            const operation = operationRunner(id, func, function * ({result, ...rest}: AsyncOperation<number>) {
                return {result: (result || 0) + 1, ...rest};
            });

            return expectSaga(operation.run)
                .run()
                .then(runResult => {
                    const result = runResult.effects.put[1].payload.action.payload.result;
                    expect(result).toBe(2);
                    expect(runResult.returnValue).toBe(1);
                });
        });
    });

    describe('createDaemon', () => {
        test('Проверяем что переданная функция вызывается с верными аргументами правильное число раз', () => {
            let result = 0;
            const actionType = 'SUM';
            const action = {type: actionType, payload: [1, 1]};
            const sum = function * (a: number, b: number) {
                result += a + b;
                return result;
            };

            return expectSaga(createDaemon, actionType, sum)
                .dispatch(action)
                .dispatch(action)
                .run({timeout: 0, silenceTimeout: true})
                .then(() => {
                    expect(result).toBe(4);
                });
        });

        test('Проверяем что демон ждет окончания операции', () => {
            const func = jest.fn(() => { /* */ });
            const actionType = 'CALL_FUNC';
            const action = {type: actionType};
            const saga = function * () {
                func();
                yield delay(10);
            };
            const main = function * () {
                yield matchers.spawn(() => createDaemon(actionType, saga));
                yield matchers.put(action);
                yield matchers.put(action);
            };

            return expectSaga(main)
                .run({timeout: 30, silenceTimeout: true})
                .then(() => {
                    expect(func).toHaveBeenCalledTimes(1);
                });
        });

        test('Проверяем что ошибка не ломает демон', () => {
            let result = 0;
            let isFirst = true;
            const actionType = 'SUM';
            const error = new Error('Exception');
            const action = {type: actionType, payload: [1, 1]};
            const sum = function * (a: number, b: number) {
                result += a + b;
                return result;
            };

            return expectSaga(createDaemon, actionType, sum)
                .provide({
                    call(effect, next) {
                        if (isFirst && effect.fn === sum) {
                            isFirst = false;
                            throw error;
                        }

                        return next();
                    }
                })
                .dispatch(action)
                .dispatch(action)
                .run({timeout: 0, silenceTimeout: true})
                .then(() => {
                    expect(result).toBe(2);
                });
        });
    });

    describe('daemonRunner', () => {
        test('Проверяем что демон запускается и слушает', () => {
            let result = 0;
            const actionType = 'SUM';
            const action = {type: actionType, payload: [1, 1]};
            const sum = function * (a: number, b: number) {
                result += a + b;
                return result;
            };
            const daemon = daemonRunner(actionType, sum);

            return expectSaga(daemon.run)
                .dispatch(action)
                .dispatch(action)
                .run({timeout: 0, silenceTimeout: true})
                .then(() => {
                    expect(result).toBe(4);
                });
        });

        test('Проверяем что демон запускается в единственном экземпляре', () => {
            let result = 0;
            const actionType = 'SUM';
            const action = {type: actionType, payload: [1, 1]};
            const sum = function * (a: number, b: number) {
                result += a + b;
                return result;
            };
            const daemon = daemonRunner(actionType, sum);
            const saga = function * () {
                yield daemon.run();
                yield daemon.run();
            };

            return expectSaga(saga)
                .dispatch(action)
                .run({timeout: 0, silenceTimeout: true})
                .then(() => {
                    expect(result).toBe(2);
                });
        });

        test('Проверяем что демон умирает', () => {
            let result = 0;
            const actionType = 'SUM';
            const action = {type: actionType, payload: [1, 1]};
            const sum = function * (a: number, b: number) {
                result += a + b;
                return result;
            };
            const daemon = daemonRunner(actionType, sum);
            const saga = function * () {
                yield daemon.run();
                yield matchers.take('KILL');
                yield daemon.destroy();
            };

            return expectSaga(saga)
                .dispatch(action)
                .dispatch({type: 'KILL'})
                .dispatch(action)
                .run()
                .then(() => {
                    expect(result).toBe(2);
                });
        });

        test('Проверяем что мод Every ловит каждый вызов', () => {
            const func = jest.fn(() => { /* */ });
            const actionType = 'CALL_FUNC';
            const action = {type: actionType};
            const saga = function * () {
                func();
                yield delay(10);
            };
            const daemon = daemonRunner(actionType, saga, {mode: DaemonMode.Every});
            const main = function * () {
                yield matchers.call(daemon.run);
                yield matchers.put(action);
                yield matchers.put(action);
            };

            return expectSaga(main)
                .run({timeout: 30, silenceTimeout: true})
                .then(() => {
                    expect(func).toHaveBeenCalledTimes(2);
                });
        });

        test('Проверяем что мод Every убивается на destroy', () => {
            const func = jest.fn(() => { /* */ });
            const actionType = 'CALL_FUNC';
            const action = {type: actionType};
            const saga = function * () { return func(); };
            const daemon = daemonRunner(actionType, saga, {mode: DaemonMode.Every});
            const main = function * () {
                yield matchers.call(daemon.run);
                yield matchers.put(action);
                yield delay(0);
                yield matchers.call(daemon.destroy);
                yield matchers.put(action);
            };

            return expectSaga(main)
                .run({timeout: 0, silenceTimeout: true})
                .then(() => {
                    expect(func).toHaveBeenCalledTimes(1);
                });
        });

        test('Проверяем что ошибка не ломает мод Every ', () => {
            let isFirst = true;
            const error = new Error('Exception');
            const func = () => { /* */ };
            const actionType = 'CALL_FUNC';
            const action = {type: actionType};
            const saga = function * () { return func(); };
            const daemon = daemonRunner(actionType, saga, {mode: DaemonMode.Every});

            return expectSaga(daemon.run)
                .provide({
                    call(effect, next) {
                        if (isFirst && effect.fn === saga) {
                            isFirst = false;
                            throw error;
                        }

                        return next();
                    }
                })
                .dispatch(action)
                .dispatch(action)
                .run({timeout: 20, silenceTimeout: true})
                .then(result => {
                    const {effects} = result;
                    const takes = effects.call.filter(e => e.payload.fn === saga);
                    expect(takes.length).toBe(2);
                });
        });

        test('Проверяем что мод Last ловит последний вызов', () => {
            const func = jest.fn((arg: any) => { /* */ });
            const actionType = 'CALL_FUNC';
            let count = 1;
            const actionCreator = () => ({type: actionType, payload: [count++]});
            const saga = function * (arg: any) {
                yield delay(10);
                func(arg);
            };
            const daemon = daemonRunner(actionType, saga, {mode: DaemonMode.Last});
            const main = function * () {
                yield matchers.call(daemon.run);
                yield matchers.put(actionCreator());
                yield matchers.put(actionCreator());
                yield matchers.put(actionCreator());
                yield matchers.put(actionCreator());
            };

            return expectSaga(main)
                .run({timeout: 30, silenceTimeout: true})
                .then(() => {
                    expect(func).toHaveBeenCalledTimes(1);
                    expect(func).toHaveBeenLastCalledWith(count - 1);
                });
        });

        test('Проверяем что мод Last убивается на destroy', () => {
            const func = jest.fn(() => { /* */ });
            const actionType = 'CALL_FUNC';
            const action = {type: actionType};
            const saga = function * () { return func(); };
            const daemon = daemonRunner(actionType, saga, {mode: DaemonMode.Last});
            const main = function * () {
                yield matchers.call(daemon.run);
                yield matchers.put(action);
                yield delay(0);
                yield matchers.call(daemon.destroy);
                yield matchers.put(action);
            };

            return expectSaga(main)
                .run({timeout: 0, silenceTimeout: true})
                .then(() => {
                    expect(func).toHaveBeenCalledTimes(1);
                });
        });

        test('Проверяем что ошибка не ломает мод Last ', () => {
            let isFirst = true;
            const error = new Error('Exception');
            const func = () => { /* */ };
            const actionType = 'CALL_FUNC';
            const action = {type: actionType};
            const saga = function * () { yield matchers.call(func); };
            const daemon = daemonRunner(actionType, saga, {mode: DaemonMode.Last});

            return expectSaga(daemon.run)
                .provide({
                    call(effect, next) {
                        if (isFirst && effect.fn === saga) {
                            isFirst = false;
                            throw error;
                        }

                        return next();
                    }
                })
                .dispatch(action)
                .dispatch(action)
                .run({timeout: 20, silenceTimeout: true})
                .then(result => {
                    const {effects} = result;
                    const calls = effects.call.filter(e => e.payload.fn === func);
                    expect(calls.length).toBe(1);
                });
        });

        test('Проверяем что мод Schedule отрабатывает по расписанию', () => {
            const timeout = 20;
            const expectedCalls = 5.5;
            const func = jest.fn((arg: any) => { /* */ });

            const daemon = daemonRunner(timeout, func, {mode: DaemonMode.Schedule});
            const main = function * () {
                yield matchers.call(daemon.run);
                yield delay(timeout * expectedCalls);
                yield matchers.call(daemon.destroy);
            };

            return expectSaga(main)
                .run({timeout: 100, silenceTimeout: true})
                .then(() => {
                    const diff = Math.ceil(expectedCalls) - func.mock.calls.length;
                    // вызывается точное число раз или на один меньше, из-за погрешностей вызова
                    expect(diff).toBeGreaterThanOrEqual(0);
                    expect(diff).toBeLessThanOrEqual(1);
                });
        });

        test('Проверяем что pattern число можно указать только с модом Schedule ', () => {
            return expectSaga(function * () {
                try {
                    return daemonRunner(5, () => { /* */ });
                } catch (e) {
                    return  e;
                }
            })
                .run({timeout: 25, silenceTimeout: true})
                .then(result => {
                    expect(result.returnValue instanceof Error).toBe(true);
                });
        });

        test('Проверяем что pattern для Schedule мода может быть функцией', () => {
            const timeout = 20;
            const expectedCalls = 5.5;
            const RESULT = {timeout};
            const func = jest.fn((arg: any) => RESULT);
            const patternFunc = (res: typeof RESULT) => res.timeout;
            const daemon = daemonRunner(patternFunc, func, {mode: DaemonMode.Schedule});
            const main = function * () {
                yield matchers.call(daemon.run);
                yield delay(timeout * expectedCalls);
                yield matchers.call(daemon.destroy);
            };
            return expectSaga(main)
                .run({timeout: 100, silenceTimeout: true})
                .then(() => {
                    const diff = Math.ceil(expectedCalls) - func.mock.calls.length;
                    // вызывается точное число раз или на один меньше, из-за погрешностей вызова
                    expect(diff).toBeGreaterThanOrEqual(0);
                    expect(diff).toBeLessThanOrEqual(expectedCalls);
                });
        });
    });
});
