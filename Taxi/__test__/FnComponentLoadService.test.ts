import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';
import {delay} from 'redux-saga/effects';
import uuid from 'uuid';

import {service} from '../services/FnComponentLoadService';

const DELAY = 10;
describe('FnComponentLoadService', () => {
    test('Проверяем что onLoad / onDispose выполняются в верном порядке', () => {
        const iterations = 15;
        let loadCounter = 0;
        let disposeCounter = 0;
        let history = '';
        const mock = jest.fn((counter: number) => counter);

        function * inc(counter: number): any {
            loadCounter++;
            history += `_${counter}l`;
            yield delay(DELAY);
        }

        function * dec(counter: number): any {
            disposeCounter++;
            mock(disposeCounter);
            history += `_${counter}d`;
            yield delay(DELAY);
        }

        const componentSaga = {onLoad: inc, onDispose: dec};
        const componentID = {};
        const operationId = 'OPERATION_ID';

        function * saga() {
            yield matchers.call(service.run);

            for (let i = 0; i < iterations; i++) {
                const loadId = `LOAD_ID_${i}`;
                yield matchers.put(service.actions.load({
                    loadId,
                    componentId: componentID,
                    operationId,
                    saga: componentSaga,
                    args: [i]
                }));
                yield delay(DELAY / 2);
                yield matchers.put(service.actions.dispose(loadId));
            }

            yield delay(DELAY / 2);
            yield matchers.call(service.destroy);
        }

        return expectSaga(saga)
            .run({timeout: iterations * 4 * DELAY})
            .then(() => {
                // колбеки вызвались равное число раз
                expect(loadCounter).toBe(disposeCounter);
                // onDispose был вызван с самыми свежими аргументами
                expect(mock).toHaveBeenLastCalledWith(loadCounter);

                const historyList = history.split('_').filter(Boolean);
                // посколку каждый цикл имеет два колбека, то всего должно быть четное число колбеков
                expect(historyList.length % 2).toBe(0);

                // проверяем по истории, что каждому лоаду соответсвовал диспоуз из того же цикла загрузки
                for (let i = 0; i < historyList.length; i += 2) {
                    const loadItem = historyList[i];
                    const disposeItem = historyList[i + 1];

                    const loadType = loadItem[loadItem.length -  1];
                    const disposeType = disposeItem[disposeItem.length -  1];
                    expect(loadType).toBe('l');
                    expect(disposeType).toBe('d');

                    const loadCounter = loadItem.substring(0, loadItem.length -  1);
                    const disposeCounter = disposeItem.substring(0, disposeItem.length -  1);
                    expect(loadCounter).toBe(disposeCounter);
                }
            });
    });

    test('Проверяем что onLoad вызывается для каждого инстанса', () => {
        const mock = jest.fn((...options: any[]) => ({}));

        function * onLoad(...args: any[]): any {
            mock(...args);
        }

        const saga = {onLoad};

        function * main() {
            yield matchers.call(service.run);

            yield matchers.put(service.actions.load({
                loadId: uuid(),
                componentId: {},
                operationId: uuid(),
                saga,
                args: ['1']
            }));

            yield delay(0);

            yield matchers.put(service.actions.load({
                loadId: uuid(),
                componentId: {},
                operationId: uuid(),
                saga,
                args: ['2']
            }));

            yield delay(DELAY);
            yield matchers.call(service.destroy);
        }

        return expectSaga(main)
            .run()
            .then(() => {
                expect(mock).toHaveBeenCalledTimes(2);
                expect(mock).toHaveBeenCalledWith('1');
                expect(mock).toHaveBeenLastCalledWith('2');
            });
    });
});
