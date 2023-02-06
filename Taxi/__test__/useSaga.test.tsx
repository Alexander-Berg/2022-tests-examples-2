import {mount} from 'enzyme';
import React from 'react';
import {Provider} from 'react-redux';
import {call, delay, select} from 'redux-saga/effects';

import useSaga from '_pkg/components/hooks/use-saga';
import store, {CommonState, sagaMiddleware} from '_pkg/infrastructure/store';
import {service} from '_pkg/sagas/services/FnComponentLoadService';

type Props = {
    x: number;
    processOperationId?: (operationId: string) => void
};

const DELAY = 10;
const processLoading = jest.fn((...args: any[]) => ({}));
const processDisposing = jest.fn((...args: any[]) => ({}));
const ARGS = ['xxx'];

const onLoad = function * (...args: [string, number]) {
    processLoading(...args);
};

const onDispose = function * (...args: [string, number]) {
    processDisposing(...args);
};

const TestComponent: React.FC<Props> = ({x, processOperationId}) => {
    const {operationId, reload} = useSaga({onLoad, onDispose}, [...ARGS, x]);

    if (processOperationId) {
        processOperationId(operationId);
    }

    return <button onClick={reload}/>;
};

const Root: React.FC<Props> = ({x, processOperationId}) => (
    <Provider store={store}>
        <TestComponent x={x} processOperationId={processOperationId}/>
    </Provider>
);

describe('useSaga', () => {
    beforeEach(() => {
        processLoading.mockClear();
        processDisposing.mockClear();
    });

    test('Saga methods were invoked with propper args', () => {
        return sagaMiddleware.run(function * () {
            yield call(service.run);

            const wrapper = mount(<Root x={1}/>);
            yield delay(DELAY);

            wrapper.setProps({x: 2});
            yield delay(DELAY);

            wrapper.unmount();
            yield delay(DELAY);

            yield call(service.destroy);
        })
            .toPromise()
            .then(() => {
                expect(processLoading).toHaveBeenCalledTimes(2);
                expect(processDisposing).toHaveBeenCalledTimes(2);

                expect(processLoading).toHaveBeenNthCalledWith(1, ...ARGS, 1);
                expect(processDisposing).toHaveBeenNthCalledWith(1, ...ARGS, 1);

                expect(processLoading).toHaveBeenNthCalledWith(2, ...ARGS, 2);
                expect(processDisposing).toHaveBeenNthCalledWith(2, ...ARGS, 2);
            });
    });

    test('useSaga creates and destroys operation', () => {
        return sagaMiddleware.run(function * () {
            yield call(service.run);
            let operationId: string;

            const processOperationId = (id: string) => operationId = id;

            const wrapper = mount(<Root x={1} processOperationId={processOperationId} />);
            yield delay(DELAY);

            let operation = yield select((state: CommonState) => state.asyncOperations[operationId]);
            expect(operation).toBeTruthy();

            wrapper.unmount();
            yield delay(DELAY);

            operation = yield select((state: CommonState) => state.asyncOperations[operationId]);
            expect(operation).toBeFalsy();

            yield call(service.destroy);
        })
            .toPromise();
    });

    test('Each Component runs it\'s own operation', () => {
        return sagaMiddleware.run(function * () {
            yield call(service.run);
            let operationId1: string | undefined;
            let operationId2: string | undefined;
            const processOperationId1 = (id: string) => operationId1 = id;
            const processOperationId2 = (id: string) => operationId2 = id;

            const wrapper = mount(
                <div>
                    <TestComponent x={1} processOperationId={processOperationId1}/>
                    <TestComponent x={2} processOperationId={processOperationId2}/>
                </div>
            );
            yield delay(DELAY);

            expect(operationId1).not.toBe(operationId2);
            expect(processLoading).toHaveBeenCalledTimes(2);
            expect(processLoading).toHaveBeenNthCalledWith(1, ...ARGS, 1);
            expect(processLoading).toHaveBeenNthCalledWith(2, ...ARGS, 2);

            wrapper.unmount();
            yield delay(DELAY);

            yield call(service.destroy);
        })
            .toPromise();
    });

    test('Reload init new load round', () => {
        return sagaMiddleware.run(function * () {
            yield call(service.run);

            const wrapper = mount(<Root x={1}/>);
            yield delay(DELAY);

            expect(processLoading).toHaveBeenCalledTimes(1);
            expect(processDisposing).toHaveBeenCalledTimes(0);

            const reloadCount = 20;
            for (let i = 0; i < reloadCount; i++) {
                wrapper.find('button').simulate('click');
            }
            yield delay(DELAY);

            expect(processDisposing).toHaveBeenCalledTimes(reloadCount);
            expect(processLoading).toHaveBeenCalledTimes(reloadCount + 1);

            wrapper.unmount();
            yield delay(DELAY);

            yield call(service.destroy);
        })
            .toPromise();
    });
});
