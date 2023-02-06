import {server} from '@yandex-taxi/callcenter-staff/bunker';
import CallcenterProvider from '@yandex-taxi/cc-jssip-hooks';
import React from 'react';

import {useProject} from '../../hooks/use-project';
import Test from './Test';

// Компонент обертка
const TestWrapper = () => {
    const project = useProject();

    return (
        <CallcenterProvider
            project={project}
            host={server.authproxyHost}
        >
            <Test/>
        </CallcenterProvider>
    );
};

export default TestWrapper;
