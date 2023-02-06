import React, {useState} from 'react';
import {v4 as uuid} from 'uuid';

import {withSaga} from 'hocs/withSaga';
import {testSaga} from 'hocs/withSaga/utils';

import FirstContainer from './FirstContainer';
import SecondContainer from './SecondContainer';
import TestComponent from './TestComponent';

const TestWrapper = () => {
    const [isShowContainer, setIsShowContainer] = useState(true);

    return (
        <div>
            {isShowContainer && <FirstContainer/>}
            <SecondContainer/>
            <TestComponent/>
            <button onClick={() => setIsShowContainer(!isShowContainer)}/>
        </div>
    );
};

TestWrapper.displayName = 'TestWrapper';

export const TestWrapperId = uuid();

export default withSaga(testSaga, {id: TestWrapperId, isRoot: true})(TestWrapper);
