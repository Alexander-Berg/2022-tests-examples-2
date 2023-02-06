import {Tab, Tabs} from 'amber-blocks/stateless-tabs';
import React, {memo} from 'react';

import {TABS} from '../../consts';
import {useTypedQuery} from '../../hooks';
import {service} from '../../sagas/services/TestingService';

/* tslint:disable: jsx-literals-restriction*/

const handleTabChange = (tab: string) => service.actions.changeTestingRoute({view: tab});

const TestingTabs: React.FC = () => {
    const {testName, view} = useTypedQuery();
    return (
        <Tabs value={view} onChange={handleTabChange}>
            <Tab value={TABS.DEBUG}>Отладка</Tab>
            <Tab value={TABS.LIST}>Список тестирования</Tab>
            <Tab value={TABS.TEST}>{testName ? `Тест (${testName})` : 'Новый тест'}</Tab>
        </Tabs>
    );
};

export default memo(TestingTabs);
