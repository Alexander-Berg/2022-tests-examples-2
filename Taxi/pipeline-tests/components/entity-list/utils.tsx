import React from 'react';

import {Col, Row} from '_blocks/row';

import {LABELS} from '../../consts';
import {CheckType, TestType} from '../../enums';
import {EnumeratedCheck, EnumeratedMocks, EnumeratedTest} from '../../types';

import {b} from './EntityItem.styl';

export const renderMockItem = (mock: EnumeratedMocks[number]) => {
    return (
        <Row gap="no" verticalAlign="center">
            <Col>{mock.name}</Col>
            <Col className={b('subtitle')}>
                {mock.resource ? `${LABELS.RESOURCE_MOCK} "${mock.resource}"` : LABELS.INPUT_MOCK}
            </Col>
        </Row>
    );
};
export const renderCheckItem = (check: EnumeratedCheck) => {
    return (
        <Row gap="no" verticalAlign="center">
            <Col>{check.name}</Col>
            <Col className={b('subtitle')}>
                {check.type === CheckType.Combined ? LABELS.COMBINED : LABELS.IMPERATIVE}
            </Col>
        </Row>
    );
};
export const renderTestItem = (test: EnumeratedTest) => {
    return (
        <Row gap="no" verticalAlign="center">
            <Col>{test.name}</Col>
            <Col className={b('subtitle')}>{test.scope === TestType.Global ? 'Global' : 'Pipeline'}</Col>
        </Row>
    );
};
