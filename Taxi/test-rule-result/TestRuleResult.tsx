import React, {memo} from 'react';

import {AmberTable, AmberTr} from '_blocks/amber-table';
import AsyncContent from '_blocks/async-content';
import {FormLayoutSimple} from '_blocks/form-layout';
import Pre from '_blocks/pre';
import {Col, Row} from '_blocks/row';
import isEmpty from '_utils/isEmpty';
import {prettyJSONStringify} from '_utils/prettyJSONStringify';

import {TestingResponse} from '../../api/types';
import {LABELS} from '../../consts';
import RulesService from '../../sagas/services/RulesService';

import {b} from './TestRuleResult.styl';

/* tslint:disable: jsx-literals-restriction*/

const DEFAULT_STATE = {isLoading: false};

const METADATA_COLS = [{title: 'Имя'}, {title: 'Значение'}];

const OK = 'ok';
const FAIL = 'fail';

const TestRuleResult: React.FC = () => {
    return (
        <AsyncContent id={RulesService.testRule.id} defaultState={DEFAULT_STATE}>
            {asyncData => {
                const data: TestingResponse = asyncData.result?.[RulesService.testRule.id!];
                if (!data) {
                    return null;
                }
                const status = data.test_result ? OK : FAIL;
                const {
                    boarding,
                    distance,
                    time,
                    waiting,
                    requirements,
                    transit_waiting,
                    destination_waiting
                } = data.output_price;
                const totalPrice =
                    boarding + distance + time + waiting + requirements + transit_waiting + destination_waiting;
                return (
                    <React.Fragment>
                        <h2 className={b('title')}>Результат тестирования:</h2>
                        <Row>
                            <Col>
                                <h3>
                                    Результат тестирования -{' '}
                                    <span className={b('status', {[status]: true})}>{status.toUpperCase()}</span>
                                </h3>
                                {data.test_error && <div className={b('error')}>{data.test_error}</div>}
                                {!isEmpty(data.metadata_map) && (
                                    <React.Fragment>
                                        <h3>Метаданные</h3>
                                        <AmberTable columns={METADATA_COLS}>
                                            {Object.keys(data.metadata_map).map(key => (
                                                <AmberTr key={key}>
                                                    <td>{key}</td>
                                                    <td>{data.metadata_map[key]}</td>
                                                </AmberTr>
                                            ))}
                                        </AmberTable>
                                    </React.Fragment>
                                )}
                            </Col>
                            <Col>
                                <h3>Выходная цена</h3>
                                <FormLayoutSimple label="boarding">{data.output_price.boarding}</FormLayoutSimple>
                                <FormLayoutSimple label="distance">{data.output_price.distance}</FormLayoutSimple>
                                <FormLayoutSimple label="time">{data.output_price.time}</FormLayoutSimple>
                                <FormLayoutSimple label="waiting">{data.output_price.waiting}</FormLayoutSimple>
                                <FormLayoutSimple label="requirements">
                                    {data.output_price.requirements}
                                </FormLayoutSimple>
                                <FormLayoutSimple label="transit_waiting">
                                    {data.output_price.transit_waiting}
                                </FormLayoutSimple>
                                <FormLayoutSimple label="destination_waiting">
                                    {data.output_price.destination_waiting}
                                </FormLayoutSimple>
                                <h3>Общая стоимость: {totalPrice}</h3>
                            </Col>
                        </Row>
                        <h3>{LABELS.EXECUTION_STATISTIC}</h3>
                        <Pre theme="transparent" lang="json" copyable>
                            {prettyJSONStringify(data?.execution_statistic)}
                        </Pre>
                    </React.Fragment>
                );
            }}
        </AsyncContent>
    );
};

export default memo(TestRuleResult);
