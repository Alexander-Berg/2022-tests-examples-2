import Button from 'amber-blocks/button';
import React, {memo, useCallback} from 'react';
import {useParams} from 'react-router-dom';

import {AmberTr} from '_blocks/amber-table';

import {TABS} from '../../consts';
import {service} from '../../sagas/services/TestingService';
import {RuleTestSummary} from '../../types';

import {b} from './TestList.styl';

/* tslint:disable: jsx-literals-restriction*/

interface Props {
    test: RuleTestSummary;
}

const TestItem: React.FC<Props> = ({test}) => {
    const {id} = useParams<{id: string}>();
    const testName = test.name;
    const goToTest = useCallback(() => service.actions.changeTestingRoute({view: TABS.TEST, testName}), [
        testName
    ]);
    const handleDelete = useCallback(() => service.actions.deleteTest(id, testName), [testName]);
    return (
        <AmberTr
            key={testName}
            className={b('test', {
                positive: test.test_result === true,
                negative: test.test_result === false
            })}
        >
            <td
                className={b('cell')}
                onClick={goToTest}
            >
                {testName}
            </td>
            <td className={b('buttonsCell')}>
                <Button onClick={handleDelete}>Удалить</Button>
            </td>
        </AmberTr>
    );
};

export default memo(TestItem);
