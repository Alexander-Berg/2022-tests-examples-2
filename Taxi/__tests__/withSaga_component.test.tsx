import {mount} from 'enzyme';
import React from 'react';

import {withSaga} from 'hocs/withSaga';

import {LoadedTasksCountsMapType} from '../types';
import {testSaga, getLoadedTasksCountsMap, clearLoadedTasks} from '../utils';

const TestElement = () => (
    <div>
        TestElement
    </div>
);

const TestSagaElement = withSaga(testSaga, {id: 'TestElement'})(TestElement);

const resultTestSagaElement: LoadedTasksCountsMapType = {
    'SagaBind(TestElement) TestElement': 1,
};

// TODO: TEWFM-906
test.skip('TestWrapper with Saga should render and have saga', () => {
    const EnzTestSagaElement = mount(<TestSagaElement/>);

    expect(getLoadedTasksCountsMap()).toEqual(resultTestSagaElement);

    EnzTestSagaElement.unmount();

    expect(getLoadedTasksCountsMap()).toEqual({});
    clearLoadedTasks();
});
