import React, {memo} from 'react';
import {v4 as uuid} from 'uuid';

import {withSaga} from 'hocs/withSaga';
import {testSaga} from 'hocs/withSaga/utils';

const TestComponent = () => (
    <div>
        TestElement
    </div>
);

TestComponent.displayName = 'TestComponent';

export const TestComponentId = uuid();

export default memo(withSaga(testSaga, {id: TestComponentId})(TestComponent) as typeof TestComponent);
