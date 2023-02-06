import React, {memo} from 'react';

import {TABS} from '../../consts';
import {useTypedQuery} from '../../hooks';
import DebugButtons from './DebugButtons';
import TestButtons from './TestButtons';
import TestListButtons from './TestListButtons';

interface Props {
    isNew?: boolean;
}

const TestingFormButtons: React.FC<Props> = ({isNew}) => {
    const {view} = useTypedQuery();
    if (isNew) {
        return <DebugButtons />;
    }
    if (view === TABS.DEBUG) {
        return <DebugButtons />;
    }
    if (view === TABS.LIST) {
        return <TestListButtons />;
    }
    if (view === TABS.TEST) {
        return <TestButtons />;
    }
    return null;
};

export default memo(TestingFormButtons);
