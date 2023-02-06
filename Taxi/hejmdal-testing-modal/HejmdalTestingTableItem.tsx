import Button from 'amber-blocks/button';
import ButtonGroup from 'amber-blocks/button-group';
import React, {memo, useCallback} from 'react';

import {AmberTr} from '_blocks/amber-table';
import ColStatus from '_blocks/cols/status';
import {AmberField} from '_blocks/form';
import {StrictModel} from '_types/common/infrastructure';

import {TEXTS} from './consts';
import {TestsListItem, TestStatus} from './types';

import {b} from './HejmdalTestingTableItem.styl';

interface Props {
    item: TestsListItem;
    model: StrictModel<boolean>;
    onRunTest: (id: number) => void;
    onDebug: (id: number) => void;
}

const STATUS_MAP: Record<TestStatus, string> = {
    [TestStatus.Success]: 'success',
    [TestStatus.Error]: 'error',
    [TestStatus.Default]: 'default'
};

export default memo<Props>(function HejmdalTestingTableItem({item, model, onRunTest, onDebug}) {
    const {id, check_type, description, status} = item;

    const handleRunTest = useCallback(() => {
        onRunTest(id);
    }, [id, onRunTest]);

    const handleDebug = useCallback(() => {
        onDebug(id);
    }, [id, onDebug]);

    return (
        <AmberTr>
            <ColStatus type={STATUS_MAP[status!]} />
            <td>
                <AmberField.checkbox model={model} />
            </td>
            <td>{id}</td>
            <td>{check_type}</td>
            <td>{description}</td>
            <td>
                <ButtonGroup className={b('actions')}>
                    <Button theme="accent" children={TEXTS.RUN_TEST} onClick={handleRunTest} />
                    <Button children={TEXTS.TO_DEBUG} onClick={handleDebug} />
                </ButtonGroup>
            </td>
        </AmberTr>
    );
});
