import {Button} from 'amber-blocks';
import Trash from 'amber-blocks/icon/Trash';
import React, {FC, memo, SyntheticEvent, useCallback, useMemo} from 'react';

import {FormCollectionField} from '_blocks/amber-form-collection';
import {AmberField, classNames} from '_blocks/form';
import {FormLayoutSimple} from '_blocks/form-layout';
import {Panel} from '_blocks/panel';
import {Col, Row} from '_blocks/row';
import {useIsFormDisabled} from '_hooks/use-is-form-disabled';
import useStrictModel from '_hooks/use-strict-model';
import {binded as commonActions} from '_infrastructure/actions';
import {THEME} from '_pkg/consts';
import {StrictModel} from '_types/common/infrastructure';
import modelPath from '_utils/modelPath';

import {LABELS} from '../../consts';
import {TestcaseMockResourceModel, TestcaseModel, TestCheckModel, TestMockModel} from '../../types';
import {makeDefaultTestcaseMockResourceModel} from '../../utils';
import ChecksSelect from '../checks-select';
import InputMockSelect from '../input-mock-select';
import MockResourceRow from './MockResourceRow';

import {b} from './TestForm.styl';

type Props = {
    model: StrictModel<TestcaseModel>;
    index: number;
    mocks: TestMockModel[];
    checks: TestCheckModel[];
    disabledRemove: boolean;
    onRemoveTestcase: (index: number) => void;
};

const TRASH_ICON = <Trash />;

const DEFAULT_RESOURCE_MOCK = makeDefaultTestcaseMockResourceModel();

const TestcaseForm: FC<Props> = ({model, index, mocks, checks, disabledRemove, onRemoveTestcase}) => {
    const path = useMemo(() => modelPath(model), [model]);

    const {resourcesMocks, testcaseName, _id} = useStrictModel(path(m => m));

    const disabled = useIsFormDisabled();

    const hideResourcesMocks = disabled && !resourcesMocks.length;

    const handleRemoveTestcase = useCallback((event: SyntheticEvent) => {
        event.stopPropagation();
        onRemoveTestcase(index);
    }, [onRemoveTestcase, index]);

    const handleRemoveMockResourceRow = useCallback(
        (rowIndex: number) => {
            commonActions.form.strict.remove(
                path(m => m.resourcesMocks),
                rowIndex,
            );
        },
        [path],
    );

    const renderMockResourceRow = useCallback(
        (_, rowIndex: number) => {
            return (
                <MockResourceRow
                    model={path(m => m.resourcesMocks[rowIndex])}
                    rowIndex={rowIndex}
                    mocks={mocks}
                    onRemoveRow={handleRemoveMockResourceRow}
                />
            );
        },
        [path, mocks, handleRemoveMockResourceRow],
    );

    const header = useMemo(() => {
        return (
            <Row gap="no" verticalAlign="center" className={b('testcaseHeader')}>
                <Col stretch>{`${LABELS.TESTCASE} ${disabled ? testcaseName : testcaseName || index + 1}`}</Col>
                <Col>
                    {!disabled && <Button icon={TRASH_ICON} onClick={handleRemoveTestcase} disabled={disabledRemove} />}
                </Col>
            </Row>
        );
    }, [index, disabled, testcaseName, handleRemoveTestcase, disabledRemove]);

    return (
        <Panel theme={THEME.WHITE} activeKey={_id} header={header}>
            <div className={b('testcaseContent')}>
                <Row nocols>
                    <FormLayoutSimple label={LABELS.NAME}>
                        <AmberField.text model={path(m => m.testcaseName)} className={classNames.field200} />
                    </FormLayoutSimple>
                </Row>
                {!hideResourcesMocks && (
                    <FormLayoutSimple label={LABELS.RESOURCES_MOCKS} flex>
                        <FormCollectionField<TestcaseMockResourceModel>
                            model={path(m => m.resourcesMocks)}
                            renderRow={renderMockResourceRow}
                            defaultRowValue={DEFAULT_RESOURCE_MOCK}
                            rowGap="s"
                            hideRemoveButton
                            stretch
                        />
                    </FormLayoutSimple>
                )}
                <FormLayoutSimple label={LABELS.INPUT_MOCK}>
                    <InputMockSelect model={path(m => m.inputMock)} mocks={mocks} className={classNames.field200} />
                </FormLayoutSimple>
                <FormLayoutSimple label={LABELS.CHECKS} flex>
                    <ChecksSelect model={path(m => m.checks)} checks={checks} multi />
                </FormLayoutSimple>
            </div>
        </Panel>
    );
};

export default memo(TestcaseForm);
