import React, {memo} from 'react';
import {v4 as uuid} from 'uuid';

import {withSaga} from 'hocs/withSaga';
import {testSaga} from 'hocs/withSaga/utils';

import TestComponent from './TestComponent';

const FirstContainer = () => (
    <div>
        <TestComponent/>
    </div>
);

FirstContainer.displayName = 'FirstContainer';

export const FirstContainerId = uuid();

export default memo(withSaga(testSaga, {id: FirstContainerId})(FirstContainer) as typeof FirstContainer);
