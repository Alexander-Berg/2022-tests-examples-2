import {mount} from 'enzyme';
import React from 'react';

import {LoadedTasksCountsMapType} from '../types';
import {getLoadedTasksCountsMap, clearLoadedTasks} from '../utils';

import {FirstContainerId} from './FirstContainer';
import {SecondContainerId} from './SecondContainer';
import {TestComponentId} from './TestComponent';
import TestSagaWrapper, {TestWrapperId} from './TestSagaWrapper';

const resultTestSagaWrapperWithContainer: LoadedTasksCountsMapType = {
    [`SagaBind(TestWrapper) ${TestWrapperId}`]: 1,
    [`SagaBind(FirstContainer) ${FirstContainerId}`]: 1,
    [`SagaBind(SecondContainer) ${SecondContainerId}`]: 1,
    [`SagaBind(TestComponent) ${TestComponentId}`]: 3,
};

const resultTestSagaWrapperWithoutContainer: LoadedTasksCountsMapType = {
    [`SagaBind(TestWrapper) ${TestWrapperId}`]: 1,
    [`SagaBind(SecondContainer) ${SecondContainerId}`]: 1,
    [`SagaBind(TestComponent) ${TestComponentId}`]: 2,
};

// TODO: TEWFM-906
test.skip('TestWrapper with Saga should render and have saga', () => {
    const EnzTestSagaWrapper = mount(<TestSagaWrapper/>);

    expect(getLoadedTasksCountsMap()).toEqual(resultTestSagaWrapperWithContainer);

    EnzTestSagaWrapper.find('button').simulate('click');

    expect(getLoadedTasksCountsMap()).toEqual(resultTestSagaWrapperWithoutContainer);

    EnzTestSagaWrapper.find('button').simulate('click');

    expect(getLoadedTasksCountsMap()).toEqual(resultTestSagaWrapperWithContainer);

    EnzTestSagaWrapper.unmount();

    expect(getLoadedTasksCountsMap()).toEqual({});
    clearLoadedTasks();
});
