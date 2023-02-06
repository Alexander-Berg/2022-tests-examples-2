import {orderBy} from 'lodash';
import React, {memo, useMemo} from 'react';

import {AmberTable, Column} from '_blocks/amber-table';

import {TEXTS} from './consts';
import HejmdalTestingResultTableItem from './HejmdalTestingResultTableItem';
import {TestResultItem} from './types';

import {b} from './HejmdalTestingResultTable.styl';

interface Props {
    tests: TestResultItem[];
    onDebug: (id: number) => void;
}

const COLUMNS: Column[] = [
    {className: b('status')},
    {title: TEXTS.ID, className: b('id')},
    {title: TEXTS.TYPE, className: b('type')},
    {title: TEXTS.DESC},
    {title: TEXTS.MESSAGE},
    {className: b('actions')}
];

export default memo<Props>(function HejmdalTestingResultTable({tests, onDebug}) {
    const ordered = useMemo(() => orderBy(tests, x => x.status), [tests]);

    return (
        <AmberTable columns={COLUMNS} sticky fixed>
            {ordered.map(test => (
                <HejmdalTestingResultTableItem key={test.test_case_id} test={test} onDebug={onDebug} />
            ))}
        </AmberTable>
    );
});
