import React, {memo} from 'react';
import {useSelector} from 'react-redux';

import {FormCollectionField} from '_blocks/amber-form-collection';
import AsyncContent from '_blocks/async-content';
import {AmberField, classNames, Form} from '_blocks/form';
import {FormLayoutCol, FormLayoutGroup, FormLayoutRow, FormLayoutSimple} from '_blocks/form-layout';
import JSONEditorField from '_blocks/form/amber-field/code-editor/JSONEditorField';
import {Col, Row} from '_blocks/row';
import useOperation from '_hooks/use-operation';
import useSaga from '_hooks/use-saga';
import {binded as commonActions} from '_infrastructure/actions';

import {LABELS, TESTING_FORM, TESTING_MODEL} from '../../consts';
import {useTypedQuery} from '../../hooks';
import TestingService from '../../sagas/services/TestingService';
import {BundleState} from '../../types';
import {testingModel} from '../../utils';
import TestResult from '../test-result';
import UserOptions from '../user-options';
import ExpectedMetadata from './ExpectedMetadata';
import ExpectedOutputPriceItem from './ExpectedOutputPriceItem';
import * as saga from './saga';

import {b} from './TestRuleForm.styl';

/* tslint:disable: jsx-literals-restriction*/

const renderRow = (rule: {key: string; value: string}, index: number, model: string) => {
    return <ExpectedMetadata metadata={rule} model={model} index={index} />;
};

interface Props {
    testName?: string;
    ruleId: string;
}

const handleModelChange = () => {
    commonActions.form.strict.change(testingModel(m => m.$meta.isTestChanged) as any, true);
};

const TestForm: React.FC<Props> = ({testName, ruleId}) => {
    const {importFrom, action, importFromOrder, source} = useTypedQuery();
    const isPristine = useSelector((state: BundleState) => state[TESTING_FORM].$form.pristine);
    const showResult = useSelector((state: BundleState) => state[TESTING_MODEL]?.$meta?.showResult);
    const isEdit = importFrom || (!action && testName !== undefined);
    const hash = useOperation({operationId: TestingService.importedTestJsonHash.id!}).result ?? '';
    const {operationId} = useSaga(saga, [ruleId, testName, importFrom, importFromOrder, source, hash]);
    return (
        <AsyncContent id={operationId}>
            <FormLayoutGroup>
                <Form
                    model={TESTING_MODEL}
                    onChange={handleModelChange}
                >
                    <FormLayoutSimple label={LABELS.PRICE_CALC_VERSION}>
                        <AmberField.text
                            model={testingModel(m => m.price_calc_version)}
                        />
                    </FormLayoutSimple>
                    <FormLayoutSimple label="Название теста">
                        <AmberField.text
                            disabled={isEdit}
                            model={testingModel(m => m.name)}
                            className={classNames.field300}
                        />
                    </FormLayoutSimple>
                    <Row>
                        <div className={b('backendVariables')}>
                            <h3>Backend variables</h3>
                            <JSONEditorField
                                height="100%"
                                className={b('backendVariablesField')}
                                model={testingModel(m => m.backend_variables)}
                            />
                        </div>
                        <Col className={classNames.field300}>
                            <h3>Детали поездки</h3>
                            <FormLayoutRow>
                                <FormLayoutCol>total_distance</FormLayoutCol>
                                <FormLayoutCol>
                                    <AmberField.text
                                        model={testingModel(m => m.trip_details.total_distance)}
                                        className={classNames.field100}
                                    />
                                </FormLayoutCol>
                            </FormLayoutRow>
                            <FormLayoutSimple label="total_time">
                                <AmberField.text
                                    model={testingModel(m => m.trip_details.total_time)}
                                    className={classNames.field100}
                                />
                            </FormLayoutSimple>
                            <FormLayoutSimple label="waiting_time">
                                <AmberField.text
                                    model={testingModel(m => m.trip_details.waiting_time)}
                                    className={classNames.field100}
                                />
                            </FormLayoutSimple>
                            <FormLayoutSimple label="wait_in_transit_time">
                                <AmberField.text
                                    model={testingModel(m => m.trip_details.waiting_in_transit_time)}
                                    className={classNames.field100}
                                />
                            </FormLayoutSimple>
                            <FormLayoutSimple label="wait_in_destination_time">
                                <AmberField.text
                                    model={testingModel(m => m.trip_details.waiting_in_destination_time)}
                                    className={classNames.field100}
                                />
                            </FormLayoutSimple>
                            <UserOptions
                                title={LABELS.USER_OPTIONS}
                                model={testingModel(m => m.trip_details.user_options)}
                            />
                            <UserOptions
                                title={LABELS.USER_META}
                                model={testingModel(m => m.trip_details.user_meta)}
                            />
                            <h3>Входная цена</h3>
                            <FormLayoutSimple label="boarding">
                                <AmberField.text
                                    model={testingModel(m => m.initial_price.boarding)}
                                    className={classNames.field100}
                                />
                            </FormLayoutSimple>
                            <FormLayoutSimple label="distance">
                                <AmberField.text
                                    model={testingModel(m => m.initial_price.distance)}
                                    className={classNames.field100}
                                />
                            </FormLayoutSimple>
                            <FormLayoutSimple label="time">
                                <AmberField.text
                                    model={testingModel(m => m.initial_price.time)}
                                    className={classNames.field100}
                                />
                            </FormLayoutSimple>
                            <FormLayoutSimple label="waiting">
                                <AmberField.text
                                    model={testingModel(m => m.initial_price.waiting)}
                                    className={classNames.field100}
                                />
                            </FormLayoutSimple>
                            <FormLayoutSimple label="requirements">
                                <AmberField.text
                                    model={testingModel(m => m.initial_price.requirements)}
                                    className={classNames.field100}
                                />
                            </FormLayoutSimple>
                            <FormLayoutSimple label="destination_waiting">
                                <AmberField.text
                                    model={testingModel(m => m.initial_price.destination_waiting)}
                                    className={classNames.field100}
                                />
                            </FormLayoutSimple>
                            <FormLayoutSimple label="transit_waiting">
                                <AmberField.text
                                    model={testingModel(m => m.initial_price.transit_waiting)}
                                    className={classNames.field100}
                                />
                            </FormLayoutSimple>
                        </Col>
                    </Row>
                    <Row>
                        <Col className={b('backendVariables')}>
                            <h3>Ожидаемые метаданные</h3>
                            <FormCollectionField model={testingModel(m => m.output_meta)} renderRow={renderRow} />
                        </Col>
                        <Col className={classNames.field300}>
                            <h3>Ожидаемая выходная цена</h3>
                            <ExpectedOutputPriceItem item="boarding" />
                            <ExpectedOutputPriceItem item="distance" />
                            <ExpectedOutputPriceItem item="time" />
                            <ExpectedOutputPriceItem item="waiting" />
                            <ExpectedOutputPriceItem item="requirements" />
                            <ExpectedOutputPriceItem item="destination_waiting" />
                            <ExpectedOutputPriceItem item="transit_waiting" />
                        </Col>
                    </Row>
                    {isPristine && <TestResult showResult={showResult} ruleId={ruleId} />}
                </Form>
            </FormLayoutGroup>
        </AsyncContent>
    );
};

export default memo(TestForm);
