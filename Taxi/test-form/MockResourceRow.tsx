import {Button} from 'amber-blocks';
import Trash from 'amber-blocks/icon/Trash';
import React, {FC, memo, useCallback, useMemo} from 'react';

import {classNames} from '_blocks/form';
import {Col, Row} from '_blocks/row';
import {useIsFormDisabled} from '_hooks/use-is-form-disabled';
import useStrictModel from '_hooks/use-strict-model';
import {StrictModel} from '_types/common/infrastructure';
import modelPath from '_utils/modelPath';

import ResourceSelect from '../../../common/components/resource-select';
import {TestcaseMockResourceModel, TestMockModel} from '../../types';
import ResourceMockSelect from '../resource-mock-select';

type Props = {
    model: StrictModel<TestcaseMockResourceModel>;
    mocks: TestMockModel[];
    rowIndex: number;
    onRemoveRow: (rowIndex: number) => void;
};

const TRASH_ICON = <Trash />;

const MockResourceRow: FC<Props> = ({model, mocks, rowIndex, onRemoveRow}) => {
    const path = useMemo(() => modelPath(model), [model]);
    const resource = useStrictModel(path(m => m.resourceName));
    const disabled = useIsFormDisabled();

    const handleRemoveRow = useCallback(() => {
        onRemoveRow(rowIndex);
    }, [onRemoveRow, rowIndex]);

    return (
        <Row gap="no" verticalAlign="top">
            <Col stretch>
                <Row gap="no" verticalAlign="top">
                    <Col>
                        <ResourceSelect
                            model={path(m => m.resourceName)}
                            className={classNames.field200}
                        />
                    </Col>
                    <Col>
                        <ResourceMockSelect
                            model={path(m => m.mockName)}
                            resource={resource}
                            mocks={mocks}
                            className={classNames.field200}
                        />
                    </Col>
                </Row>
            </Col>
            {!disabled && (
                <Col>
                    <Button icon={TRASH_ICON} onClick={handleRemoveRow} />
                </Col>
            )}
        </Row>
    );
};

export default memo(MockResourceRow);
