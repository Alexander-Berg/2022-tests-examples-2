import Checkbox from 'amber-blocks/checkbox';
import React, {memo, useCallback, useEffect, useMemo, useState} from 'react';

import {AmberTable, Column} from '_blocks/amber-table';
import useStrictModel from '_hooks/use-strict-model';
import {binded as commonActions} from '_infrastructure/actions';
import {StrictModel} from '_types/common/infrastructure';
import objectKeys from '_utils/objectKeys';

import {TEXTS} from './consts';
import HejmdalTestingTableItem from './HejmdalTestingTableItem';
import {SelectedMap, TestsListItem} from './types';
import {createSelectedPath} from './utils';

import {b} from './HejmdalTestingTable.styl';

interface Props {
    items: TestsListItem[];
    model: StrictModel<SelectedMap>;
    onRunTest: (id: number) => void;
    onDebug: (id: number) => void;
}

interface CheckboxProps {
    model: StrictModel<SelectedMap>;
}

const SelectAllCheckbox = memo<CheckboxProps>(function SelectAllCheckbox({model}) {
    const selectedTests = useStrictModel(model);
    const [checked, setChecked] = useState(false);

    const total = Object.keys(selectedTests).length;
    const active = Object.values(selectedTests).filter(Boolean).length;
    const indeterminate = active !== 0 && active !== total;

    useEffect(() => {
        setChecked(active === total);
    }, [active, total]);

    const handleCheck = useCallback(() => {
        const value = objectKeys(selectedTests).reduce<SelectedMap>((result, key) => {
            result[key] = !checked;
            return result;
        }, {});

        commonActions.form.change(model, value);
    }, [checked]);

    return <Checkbox checked={checked} indeterminate={indeterminate} onChange={handleCheck} />;
});

function createColumns(model: StrictModel<SelectedMap>): Column[] {
    return [
        {className: b('status')},
        {title: <SelectAllCheckbox model={model} />, className: b('checkbox')},
        {title: TEXTS.ID, className: b('id')},
        {title: TEXTS.TYPE, className: b('type')},
        {title: TEXTS.DESC},
        {className: b('actions')}
    ];
}

export default memo<Props>(function HejmdalTestingTable({items, model, onRunTest, onDebug}) {
    const path = useMemo(() => createSelectedPath(model), [model]);
    const columns = useMemo(() => createColumns(model), [model]);

    return (
        <AmberTable columns={columns} fixed sticky>
            {items.map(item => (
                <HejmdalTestingTableItem
                    key={item.id}
                    item={item}
                    model={path(m => m[item.id])}
                    onRunTest={onRunTest}
                    onDebug={onDebug}
                />
            ))}
        </AmberTable>
    );
});
