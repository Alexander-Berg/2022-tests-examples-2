import isEmpty from 'lodash/isEmpty';
import React, {memo, useMemo} from 'react';
import {useSelector} from 'react-redux';

import {AmberTable} from '_blocks/amber-table';
import AsyncContent from '_blocks/async-content';
import {classNames} from '_blocks/form';
import Pre from '_blocks/pre';
import {Col, Row} from '_blocks/row';
import useOperation from '_hooks/use-operation';
import {getOperation} from '_infrastructure/selectors';
import {prettyJSONStringify} from '_utils/prettyJSONStringify';

import {LABELS} from '../../consts';
import TestingService from '../../sagas/services/TestingService';
import OutputMetadata from './OutputMetadata';
import OutputPrice from './OutputPrice';

import {b} from './TestResult.styl';

/* tslint:disable: jsx-literals-restriction*/

const DEFAULT_STATE = {isLoading: false};

const METADATA_COLS = [{title: 'Имя'}, {title: 'Значение'}];

const OK = 'ok';
const FAIL = 'fail';

interface Props {
    showResult?: boolean;
    ruleId: string;
}

const TestResult: React.FC<Props> = ({showResult, ruleId}) => {
    const operationSelector = getOperation(TestingService.getTest.id);
    const getTestOperation = useSelector(operationSelector);
    const runTestOperation = useOperation({operationId: TestingService.runTest.id!});
    const data = runTestOperation.result;
    const status = data?.result ? OK : FAIL;

    const totalPrice = useMemo(() => {
        const {
            boarding = 0,
            distance = 0,
            time = 0,
            waiting = 0,
            requirements = 0,
            transit_waiting = 0,
            destination_waiting = 0,
        } = data?.output_price || {};
        return boarding + distance + time + waiting + requirements + transit_waiting + destination_waiting;
    }, [data?.output_price]);
    if (!showResult || !data) {
        const status = getTestOperation?.result?.last_result ? OK : FAIL;
        return getTestOperation?.args?.[1] === ruleId && getTestOperation?.result?.last_result !== undefined ? (
            <React.Fragment>
                <h2 className={b('title')}>
                    <span>Результат тестирования</span>
                    <span className={b('status', {[status]: true})}>{status.toUpperCase()}</span>
                </h2>
            </React.Fragment>
        ) : null;
    }
    return (
        <AsyncContent id={[TestingService.runTest.id!, TestingService.getTest.id!]} defaultState={DEFAULT_STATE}>
            <h2 className={b('title')}>
                <span>Результат тестирования</span>
                <span className={b('status', {[status]: true})}>{status.toUpperCase()}</span>
            </h2>
            {data?.error && <div className={b('error')}>{data.error}</div>}
            {data?.output_price && (
                <Row>
                    <Col className={b('metadata')}>
                        {!isEmpty(data?.metadata_map) && (
                            <React.Fragment>
                                <h3>Метаданные</h3>
                                <AmberTable columns={METADATA_COLS} hasHead={false}>
                                    {Object.keys(data.metadata_map || {}).map(key => (
                                        <OutputMetadata key={key} data={data} item={key} />
                                    ))}
                                </AmberTable>
                            </React.Fragment>
                        )}
                    </Col>
                    <Col className={classNames.field300}>
                        <h3>Выходная цена</h3>
                        <OutputPrice data={data} item="boarding" />
                        <OutputPrice data={data} item="distance" />
                        <OutputPrice data={data} item="time" />
                        <OutputPrice data={data} item="waiting" />
                        <OutputPrice data={data} item="requirements" />
                        <OutputPrice data={data} item="transit_waiting" />
                        <OutputPrice data={data} item="destination_waiting" />
                        <h3>Общая стоимость: {totalPrice}</h3>
                    </Col>
                </Row>
            )}
            <h3>{LABELS.EXECUTION_STATISTIC}</h3>
            <Pre theme="transparent" lang="json" copyable>
                {prettyJSONStringify(data?.execution_statistic)}
            </Pre>
        </AsyncContent>
    );
};

export default memo(TestResult);
