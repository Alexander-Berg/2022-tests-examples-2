import {Button} from 'amber-blocks';
import ChevronDown from 'amber-blocks/icon/ChevronDown';
import Plus from 'amber-blocks/icon/Plus';
import React, {FC, memo, useCallback, useMemo} from 'react';

import {FormCollectionField} from '_blocks/amber-form-collection';
import {AmberField, Form} from '_blocks/form';
import {FormLayoutSimple} from '_blocks/form-layout';
import {PanelGroup} from '_blocks/panel';
import {Col, Row} from '_blocks/row';
import {useIsFormDisabled} from '_hooks/use-is-form-disabled';
import useStrictModel from '_hooks/use-strict-model';
import {binded as commonActions} from '_infrastructure/actions';
import GroupFields from '_pkg/blocks/group-fields';
import {StrictModel} from '_types/common/infrastructure';
import modelPath from '_utils/modelPath';
import {toNumber} from '_utils/strict/parser';
import {isNotEmpty} from '_utils/strict/validators';

import {LABELS} from '../../consts';
import {TestSubmode, TestType} from '../../enums';
import {TestcaseModel, TestModel} from '../../types';
import {makeDefaultTestcaseModel} from '../../utils';
import EntityList from '../entity-list';
import {renderCheckItem, renderMockItem} from '../entity-list/utils';
import TestcaseForm from './TestcaseForm';

import {b} from './TestForm.styl';

type Props = {
    model: StrictModel<TestModel>;
    hideContent: boolean;
    toggleContent: () => void;
    onSetSubmode: (submode: TestSubmode, editIndex: number) => void;
};

const PLUS_ICON = <Plus />;

const OPTIONS = [
    {label: LABELS.PIPELINE, value: TestType.Pipeline},
    {label: LABELS.GLOBAL, value: TestType.Global},
];

const TestForm: FC<Props> = ({model, hideContent, toggleContent, onSetSubmode}) => {
    const path = useMemo(() => modelPath(model), [model]);

    const disabled = useIsFormDisabled();

    const {mocks, checks, testcases} = useStrictModel(model);

    const mockItems = useMemo(
        () =>
            mocks.map(({mockName, resource}, index) => ({
                id: index.toString(),
                name: mockName,
                resource,
            })),
        [mocks],
    );

    const checkItems = useMemo(
        () =>
            checks.map(({checkName}, index) => ({
                id: index.toString(),
                name: checkName,
            })),
        [checks],
    );

    const handleAddMock = useCallback(() => {
        onSetSubmode(TestSubmode.MockEdit, mocks.length);
    }, [onSetSubmode, mocks.length]);

    const handleAddCheck = useCallback(() => {
        onSetSubmode(TestSubmode.CheckEdit, checks.length);
    }, [onSetSubmode, checks.length]);

    const handleEditMock = useCallback(
        (index: string) => {
            onSetSubmode(TestSubmode.MockEdit, toNumber(index));
        },
        [onSetSubmode],
    );

    const handleEditCheck = useCallback(
        (index: string) => {
            onSetSubmode(TestSubmode.CheckEdit, toNumber(index));
        },
        [onSetSubmode],
    );

    const handleRemoveMock = useCallback(
        (index: string) => {
            commonActions.form.strict.remove(
                path(m => m.mocks),
                toNumber(index),
            );
        },
        [path],
    );

    const handleRemoveCheck = useCallback(
        (index: string) => {
            commonActions.form.strict.remove(
                path(m => m.checks),
                toNumber(index),
            );
        },
        [path],
    );

    const handleAddTestcase = useCallback(() => {
        commonActions.form.strict.push(
            path(m => m.testcases),
            makeDefaultTestcaseModel(),
        );
    }, [path]);

    const handleRemoveTestcase = useCallback(
        (index: number) => {
            commonActions.form.strict.remove(
                path(m => m.testcases),
                index,
            );
        },
        [path],
    );

    const renderRow = useCallback(
        (_, index: number) => {
            return (
                <TestcaseForm
                    model={path(m => m.testcases[index])}
                    index={index}
                    onRemoveTestcase={handleRemoveTestcase}
                    mocks={mocks}
                    checks={checks}
                    disabledRemove={testcases.length <= 1}
                />
            );
        },
        [path, mocks, checks, testcases, handleRemoveTestcase],
    );

    return (
        <Form model={model}>
            <FormLayoutSimple label={LABELS.NAME}>
                <AmberField.text model={path(m => m.testName)} />
            </FormLayoutSimple>
            <FormLayoutSimple label={LABELS.SCOPE} flex>
                <AmberField.radioButton model={path(m => m.testType)} options={OPTIONS} />
            </FormLayoutSimple>
            <GroupFields className={b('groupFields')} contentClassName={b('groupFieldsContent')}>
                <Row
                    className={b('testcaseHeader', {showBorder: !hideContent, pointer: true})}
                    verticalAlign="center"
                    onClick={toggleContent}
                    gap="no"
                >
                    <Col className={b('iconCol', {right: hideContent})}>
                        <ChevronDown />
                    </Col>
                    <Col stretch>{LABELS.MOCKS_AND_CHECKS_IN_TEST}</Col>
                    <Col className={b('testcaseHeaderAdditional')}>
                        {`${LABELS.MOCKS}: ${mocks.length}, ${LABELS.CHECKS}: ${checks.length}`}
                    </Col>
                </Row>
                {!hideContent && (
                    <Row nocols gap="no" className={b('entitiesContent')}>
                        <Row nocols gap="l">
                            <Row nocols>{LABELS.MOCKS}</Row>
                            <EntityList
                                items={mockItems}
                                renderItem={renderMockItem}
                                onRemove={handleRemoveMock}
                                onRowClick={handleEditMock}
                                isDarkRow
                            />
                            {!disabled && <Button icon={PLUS_ICON} onClick={handleAddMock} />}
                        </Row>

                        <Row nocols>{LABELS.CHECKS}</Row>
                        <EntityList
                            items={checkItems}
                            renderItem={renderCheckItem}
                            onRemove={handleRemoveCheck}
                            onRowClick={handleEditCheck}
                            isDarkRow
                        />
                        {!disabled && <Button icon={PLUS_ICON} onClick={handleAddCheck} />}
                    </Row>
                )}
            </GroupFields>
            <Row className={b('subHeader')} nocols>
                {LABELS.TESTCASES}
            </Row>
            {isNotEmpty(testcases) && (
                <PanelGroup multiSelect>
                    <FormCollectionField<TestcaseModel>
                        model={path(m => m.testcases)}
                        renderRow={renderRow}
                        rowGap="s"
                        stretch
                        hideRemoveButton
                        hideAddButton
                    />
                </PanelGroup>
            )}
            {!disabled && (
                <Button className={b('plusButton')} iconStart={PLUS_ICON} onClick={handleAddTestcase}>
                    {LABELS.TESTCASE}
                </Button>
            )}
        </Form>
    );
};

export default memo(TestForm);
