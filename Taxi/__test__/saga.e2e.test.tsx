import {mount} from 'enzyme';
import React, {useEffect, useState} from 'react';
import {Provider} from 'react-redux';
import {call, delay, take} from 'redux-saga/effects';

import {Action, AsyncOperation} from '_types/common/infrastructure';

import AsyncContent from '_pkg/components/blocks/async-content';
import useSaga from '_pkg/components/hooks/use-saga';
import store, {sagaMiddleware} from '_pkg/infrastructure/store';
import {constants} from '_pkg/reducers/asyncOperations';
import {operation} from '_pkg/sagas/decorators';
import {service} from '_pkg/sagas/services/FnComponentLoadService';
import createPaginationStrategy from '_pkg/sagas/update-strategies/paginationStrategy';
import {createService} from '_pkg/sagas/utils';

import useService from '../use-service';

const DELAY = 10;

function * awaitOperation(operationId: string) {
    yield take(
        (action: Action<AsyncOperation>) => (
            action.type === constants.ADD_OR_UPDATE_OPERATION &&
            action.payload?.id === operationId &&
            action.payload?.isLoading === false
        )
    );
}

test('Cycle load dependency', () => {
    return sagaMiddleware.run(function * () {
        yield call(service.run);
        const innerLoadMock = jest.fn();
        const innerDisposeMock = jest.fn();

        class TestRequestService {
            @operation({
                updateStrategy: createPaginationStrategy<number[]>()
            })
            public static * makeRequest(...args: any[]) {
                yield delay(DELAY);
                yield call(innerLoadMock);
                return [1];
            }
        }

        const testRequestService = createService(TestRequestService, {
            onBeforeRun: function * () {
                yield delay(DELAY);
            }
        });

        function * innerLoad(...args: any[]) {
            yield call(TestRequestService.makeRequest, {reset: true});
        }

        function * innerDispose(...args: any[]) {
            yield call(innerDisposeMock, ...args);
        }

        let innerOperation: string | undefined;
        const Inner: React.FC<{setVal: Function, x: number}> = ({setVal, x}) => {
            const {operationId} = useSaga({onLoad: innerLoad, onDispose: innerDispose}, [x]);
            innerOperation = operationId;

            useEffect(() => {
                if (x > 0) {
                    setVal('1');
                }
            }, [x]);

            return <div/>;
        };

        let outerOperation: string | undefined;
        const Outer: React.FC<{x: number}> = ({x}) => {
            const [val, setVal] = useState('0');
            const {operationId} = useService(testRequestService, [val]);
            outerOperation = operationId;

            return (
                <Provider store={store}>
                    <AsyncContent id={operationId}>
                        <Inner x={x} setVal={setVal}/>
                    </AsyncContent>
                </Provider>
            );
        };

        const wrapper = mount(<Outer x={0} />);

        if (!outerOperation) {
            throw new Error('No outerOperation');
        }

        // дожидаемся загрузки сначала Outer затем Inner
        yield awaitOperation(outerOperation);

        if (!innerOperation) {
            throw new Error('No innerOperation');
        }

        yield awaitOperation(innerOperation);

        expect(innerLoadMock).toHaveBeenCalledTimes(1);
        expect(innerDisposeMock).toHaveBeenCalledTimes(0);
        expect(
            store.getState().asyncOperations[(TestRequestService.makeRequest as any).id].result
        ).toEqual([1]);

        innerLoadMock.mockClear();
        innerDisposeMock.mockClear();
        wrapper.setProps({x: 1});

        yield awaitOperation(outerOperation);
        yield awaitOperation(innerOperation);

        expect(innerLoadMock).toHaveBeenCalledTimes(1);
        expect(innerDisposeMock).toHaveBeenCalledTimes(2);
        expect(
            store.getState().asyncOperations[(TestRequestService.makeRequest as any).id].result
        ).toEqual([1]);

        wrapper.unmount();
        yield call(service.destroy);
    })
        .toPromise();
});
