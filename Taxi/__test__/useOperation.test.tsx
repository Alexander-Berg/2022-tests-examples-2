import {mount} from 'enzyme';
import React from 'react';
import {Provider} from 'react-redux';

import useOperation from '_pkg/components/hooks/use-operation';
import store from '_pkg/infrastructure/store';
import {actions} from '_pkg/reducers/asyncOperations';
import {AsyncOperation} from '_types/common/infrastructure';

const binded = store.bindActions(actions);
let wrapper: ReturnType<typeof mount>;

const OPERATION_ID = 'OPERATION_ID';
let OPERATION: AsyncOperation<string>;

describe('useOperation', () => {
    beforeEach(() => {
        OPERATION = {
            id: OPERATION_ID,
            result: 'result',
            isError: false,
            isLoading: false,
            error: undefined,
            args: []
        };
    });

    afterEach(() => {
        wrapper.unmount();
    });

    test('Component gets the operation', () => {
        binded.addOrUpdateOperation(OPERATION);

        const TestComponent: React.FC<{}> = () => {
            const operation = useOperation<string>({operationId: OPERATION_ID});

            expect(operation).toEqual(OPERATION);
            return <span>{operation.result}</span>;
        };

        wrapper = mount(
            <Provider store={store}>
                <TestComponent />
            </Provider>
        );
    });

    test('Default state is applied', () => {
        binded.removeOperation(OPERATION_ID);

        const TestComponent: React.FC<{}> = () => {
            const operation = useOperation<string>({
                operationId: OPERATION_ID,
                defaultState: {result: 'xxx'}
            });

            expect(operation.result).toEqual('xxx');
            return <span>{operation.result}</span>;
        };

        wrapper = mount(
            <Provider store={store}>
                <TestComponent />
            </Provider>
        );
    });

    test('No errors when no operation and no default state', () => {
        binded.removeOperation(OPERATION_ID);

        const TestComponent: React.FC<{}> = () => {
            const operation = useOperation<string>({
                operationId: OPERATION_ID,
                defaultState: null
            });

            return <span>{operation?.result}</span>;
        };

        wrapper = mount(
            <Provider store={store}>
                <TestComponent />
            </Provider>
        );
    });

    test('Component updates on operation changed', () => {
        binded.addOrUpdateOperation(OPERATION);
        const func = jest.fn((isLoading: boolean | undefined) => ({}));

        const TestComponent: React.FC<{}> = () => {
            const operation = useOperation<string>({operationId: OPERATION_ID});

            func(operation?.isLoading);
            return <span>{operation.result}</span>;
        };

        wrapper = mount(
            <Provider store={store}>
                <TestComponent />
            </Provider>
        );

        binded.addOrUpdateOperation({id: OPERATION_ID, isLoading: true});
        binded.addOrUpdateOperation({id: OPERATION_ID, isLoading: false});

        expect(func).toBeCalledTimes(3);
        expect(func).toHaveBeenNthCalledWith(2, true);
        expect(func).toHaveBeenNthCalledWith(3, false);
    });

    test('Component throws promise when suspense is true and operation is loading', () => {
        binded.addOrUpdateOperation(OPERATION);

        const TestComponent: React.FC<{}> = () => {
            const operation = useOperation<string>({operationId: OPERATION_ID, suspense: true});
            return <span>{operation.result}</span>;
        };

        wrapper = mount(
            <Provider store={store}>
                <TestComponent />
            </Provider>
        );

        try {
            binded.addOrUpdateOperation({
                id: OPERATION_ID,
                isLoading: true,
                promise: new Promise(() => {
                    //
                })
            });
        } catch (e) {
            expect(e.message.includes('no fallback')).toBe(true);
            return;
        }

        throw new Error('Promise was not thrown');
    });

    // TODO blocked by https://github.com/airbnb/enzyme/issues/2205
    // test('Component renders after the longest operation is completed', async () => {
    //     const operationsIds = ['OPERATION_1', 'OPERATION_2'];
    //     binded.addOrUpdateOperation({...OPERATION, id: operationsIds[0], isLoading: true});
    //     binded.addOrUpdateOperation({...OPERATION, id: operationsIds[1], isLoading: true});

    //     const TestComponent: React.FC<{}> = () => {
    //         const operation1 = useOperation<string>({operationId: operationsIds[0], suspense: true});
    //         const operation2 = useOperation<string>({operationId: operationsIds[1], suspense: true});

    //         expect(operation1.isLoading).toBe(false);
    //         expect(operation2.isLoading).toBe(false);
    //         expect(Date.now() - start).toBeGreaterThanOrEqual(100);

    //         return null;
    //     };

    //     const start = Date.now();
    //     wrapper = mount(
    //         <Provider store={store}>
    //             <Suspense fallback="Loading...">
    //                 <TestComponent/>
    //             </Suspense>
    //         </Provider>
    //     );

    //     await timeout(50);
    //     binded.addOrUpdateOperation({id: operationsIds[0], isLoading: false});
    //     await timeout(50);
    //     binded.addOrUpdateOperation({id: operationsIds[1], isLoading: false});
    // });
});
