import isEmpty from 'lodash/isEmpty';
import React, {memo} from 'react';
import {useParams} from 'react-router-dom';

import {AmberTable} from '_blocks/amber-table';
import AsyncContent from '_blocks/async-content';
import useOperation from '_hooks/use-operation';
import useSaga from '_hooks/use-saga';

import TestingService from '../../sagas/services/TestingService';
import {RouteParams} from '../../types';
import * as saga from './saga';
import TestItem from './TestItem';

/* tslint:disable: jsx-literals-restriction*/

const TestList: React.FC = () => {
    const {id} = useParams<RouteParams>();
    useSaga(saga, [id]);
    const operationId = TestingService.getRuleTests.id!;
    const operation = useOperation({operationId});
    return (
        <AsyncContent id={operationId}>
            {isEmpty(operation?.result) ? (
                <h3>Для данного правила пока нет тестов</h3>
            ) : (
                <AmberTable hasHead={false}>
                    {operation?.result?.map(test => (
                        <TestItem key={test.name} test={test} />
                    ))}
                </AmberTable>
            )}
        </AsyncContent>
    );
};

export default memo(TestList);
