import Button from 'amber-blocks/button';
import React, {memo, useCallback} from 'react';

import {AmberTr} from '_blocks/amber-table';
import ColStatus from '_blocks/cols/status';

import {TEXTS} from './consts';
import {TestResultItem, TestStatus} from './types';

interface Props {
    test: TestResultItem;
    onDebug: (id: number) => void;
}

const STATUS_MAP: Record<TestStatus, string> = {
    [TestStatus.Success]: 'success',
    [TestStatus.Error]: 'error',
    [TestStatus.Default]: 'default'
};

export default memo<Props>(function HejmdalTestingResultTableItem({test, onDebug}) {
    const {status, test_case_id, check_type, description, error_message} = test;

    const handleDebug = useCallback(() => {
        onDebug(test_case_id);
    }, [test_case_id, onDebug]);

    return (
        <AmberTr>
            <ColStatus type={STATUS_MAP[status!]} />
            <td>{test_case_id}</td>
            <td>{check_type}</td>
            <td>{description}</td>
            <td>{error_message}</td>
            <td>
                <Button children={TEXTS.DEBUG} onClick={handleDebug} />
            </td>
        </AmberTr>
    );
});
