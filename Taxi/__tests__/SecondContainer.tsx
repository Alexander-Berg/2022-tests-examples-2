import React, {memo} from 'react';
import {v4 as uuid} from 'uuid';

import {withSaga} from 'hocs/withSaga';
import {testSaga} from 'hocs/withSaga/utils';

import TestComponent from './TestComponent';

const SecondContainer = () => (
    <div>
        <TestComponent/>
    </div>
);

SecondContainer.displayName = 'SecondContainer';

export const SecondContainerId = uuid();

export default memo(withSaga(testSaga, {id: SecondContainerId})(SecondContainer) as typeof SecondContainer);
