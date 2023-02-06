import {mount} from 'enzyme';
import React, {useState} from 'react';

import {withSaga} from 'hocs/withSaga';

import {LoadedTasksCountsMapType} from '../types';
import {testSaga, getLoadedTasksCountsMap, clearLoadedTasks} from '../utils';

const TestElement = () => (
    <div>
        TestElement
    </div>
);

const TestSagaElement = withSaga(testSaga, {id: 'TestElement'})(TestElement);

const TestContainer = () => (
    <div>
        <TestSagaElement/>
    </div>
);

const TestSagaContainer = withSaga(testSaga, {id: 'TestContainer'})(TestContainer);

const TestWrapper = () => {
    const [isShowContainer, setIsShowContainer] = useState(true);

    return (
        <div>
            {isShowContainer && <TestSagaContainer/>}
            <TestSagaElement/>
            <button onClick={() => setIsShowContainer(false)}/>
        </div>
    );
};

const TestSagaWrapper = withSaga(testSaga, {id: 'TestWrapper', isRoot: true})(TestWrapper);

const resultTestSagaWrapperWithContainer: LoadedTasksCountsMapType = {
    'SagaBind(TestWrapper) TestWrapper': 1,
    'SagaBind(TestContainer) TestContainer': 1,
    'SagaBind(TestElement) TestElement': 2,
};

const resultTestSagaWrapperWithoutContainer: LoadedTasksCountsMapType = {
    'SagaBind(TestWrapper) TestWrapper': 1,
    'SagaBind(TestElement) TestElement': 1,
};

// TODO: TEWFM-906
test.skip('TestWrapper with Saga should render and have saga', () => {
    const EnzTestSagaWrapper = mount(<TestSagaWrapper/>);

    expect(getLoadedTasksCountsMap()).toEqual(resultTestSagaWrapperWithContainer);

    EnzTestSagaWrapper.find('button').simulate('click');

    expect(getLoadedTasksCountsMap()).toEqual(resultTestSagaWrapperWithoutContainer);

    EnzTestSagaWrapper.unmount();

    expect(getLoadedTasksCountsMap()).toEqual({});
    clearLoadedTasks();
});
