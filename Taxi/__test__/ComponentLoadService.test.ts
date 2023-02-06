import {Task} from 'redux-saga';
import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';
import {delay} from 'redux-saga/effects';

import {EMPTY_FLOW} from '_pkg/sagas/utils';

import ComponentLoadService, {LOAD_QUEUE, service, waitForDispose} from '../services/ComponentLoadService';

const DELAY = 10;

const cleanLoadQueue = () => {
    while (LOAD_QUEUE.length) {
        LOAD_QUEUE.pop();
    }
};

describe('ComponentLoadService', () => {
    beforeEach(() => {
        cleanLoadQueue();
    });

    test('Проверяем что waitForDispose завершается получая нужный loadId', () => {
        const loadId = 'LOAD_ID';
        let waitCompete = false;

        function * waiter() {
            yield matchers.call(waitForDispose, loadId);
            waitCompete = true;
        }

        function * saga() {
            yield matchers.fork(waiter);
        }

        return expectSaga(saga)
            .dispatch(service.actions.dispose(loadId))
            .run()
            .then(() => {
                expect(waitCompete).toBe(true);
            });
    });

    test('Проверяем что запущеный сервис ставит запросы в очередь', () => {
        const loadId = 'LOAD_ID';

        function * saga() {
            yield matchers.call(service.run);
            yield matchers.put(service.actions.load({
                loadId,
                saga: EMPTY_FLOW,
                args: null
            }));
            yield delay(0);
            yield matchers.call(service.destroy);
        }

        return expectSaga(saga)
            .run()
            .then(() => {
                expect(LOAD_QUEUE.length).toBe(1);
                expect(LOAD_QUEUE[0].saga).toBe(EMPTY_FLOW);
            });
    });

    test('Проверяем что запущеный сервис удаляет запросы из очереди', () => {
        const loadId = 'LOAD_ID';

        function * saga() {
            yield matchers.call(service.run);
            yield matchers.put(service.actions.load({
                loadId,
                saga: EMPTY_FLOW,
                args: null
            }));
            yield matchers.put(service.actions.dispose(loadId));
            yield delay(0);
            yield matchers.call(service.destroy);
        }

        return expectSaga(saga)
            .run()
            .then(() => {
                expect(LOAD_QUEUE.length).toBe(0);
            });
    });

    test('Проверяем что onLoad / onDispose выполняются в верном порядке', () => {
        const loadId = 'LOAD_ID';
        const iterations = 50;
        let loadCounter = 0;
        let disposeCounter = 0;
        let history = '';
        const mock = jest.fn((counter: number) => counter);

        function * inc(): any {
            history += `_${loadCounter++}l`;
            yield delay(DELAY);
        }

        function * dec(options: any): any {
            mock(options.args);
            history += `_${disposeCounter++}d`;
            yield delay(DELAY);
        }

        function * main() {
            yield matchers.fork(() => ComponentLoadService.basicFlow(main, inc, dec));
        }

        function * saga() {
            yield matchers.call(service.run);
            const task: Task = yield matchers.fork(() => main());

            for (let i = 0; i < iterations; i++) {
                yield matchers.put(service.actions.load({
                    loadId,
                    saga: main,
                    args: loadCounter
                }));
                yield delay(DELAY / 2);
                yield matchers.put(service.actions.dispose(loadId));
            }

            yield delay(DELAY / 2);
            yield matchers.call(service.destroy);
            task.cancel();
        }

        return expectSaga(saga as Saga)
            .run({timeout: iterations * 4 * DELAY})
            .then(() => {
                // колбеки вызвались равное число раз
                expect(loadCounter).toBe(disposeCounter);
                // последним был onDispose
                expect(history[history.length - 1]).toBe('d');
                // onDispose был вызван с самыми свежими аргументами
                expect(mock).toHaveBeenLastCalledWith(loadCounter - 1);
            });
    });

    test('Проверяем что onLoad вызывается для каждого инстанса', () => {
        const mock = jest.fn((options: any) => ({}));

        function * onLoad(options: any): any {
            mock(options.args);
        }

        function * main() {
            yield matchers.fork(() => ComponentLoadService.basicFlow(main, onLoad, EMPTY_FLOW));
        }

        function * saga() {
            yield matchers.call(service.run);
            const task: Task = yield matchers.fork(() => main());

            yield matchers.put(service.actions.load({
                loadId: '1',
                saga: main,
                args: '1'
            }));

            yield delay(0);

            yield matchers.put(service.actions.load({
                loadId: '2',
                saga: main,
                args: '2'
            }));

            yield delay(DELAY);
            yield matchers.call(service.destroy);
            task.cancel();
        }

        return expectSaga(saga as Saga)
            .run()
            .then(() => {
                expect(mock).toHaveBeenCalledTimes(2);
                expect(mock).toHaveBeenCalledWith('1');
                expect(mock).toHaveBeenLastCalledWith('2');
            });
    });
});
