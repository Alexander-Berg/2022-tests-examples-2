import Checkbox from 'amber-blocks/checkbox/Checkbox';
import React, {FC, memo} from 'react';

import AsyncContent from '_blocks/async-content';
import {AmberField} from '_blocks/form';
import {Col, Row} from '_blocks/row';
import modelStoreExtention from '_hocs/model-store-extention';
import useOperation from '_hooks/use-operation';
import useSaga from '_hooks/use-saga';

import {LABELS, TESTS_MODEL} from '../../consts';
import PipelineService from '../../sagas/services/PipelineService';
import {testsModel} from '../../utils';
import {saga} from './saga';
import TestResult from './TestResult';

import {b} from './PipelineTests.styl';

type Props = {
    name?: string;
};

const PipelineTests: FC<Props> = ({name}) => {
    const {operationId} = useSaga(saga, []);
    const {result: [globalTests, pipelineTests] = [[], []]} = useOperation({
        operationId: PipelineService.loadAllTests.id!,
    });
    const {result} = useOperation({operationId: PipelineService.loadTestsResult.id!});

    return (
        <AsyncContent id={operationId}>
            <Row gap="l">
                <Col className={b('subheader')}>{`${LABELS.PIPELINE_NAME}: ${name}`}</Col>
            </Row>
            <AsyncContent id={PipelineService.loadTestsResult.id!}>
                {result && <TestResult result={result} />}
            </AsyncContent>
            <Row className={b('title')}>{LABELS.GLOBAL_TESTS}</Row>
            <Row nocols gap="l">
                {globalTests.map(test => (
                    <Row nocols gap="s" key={test.id}>
                        <Checkbox label={test.name} checked disabled />
                    </Row>
                )) ?? LABELS.TESTS_NOT_CREATED}
            </Row>
            <Row className={b('title')}>{LABELS.PIPELINE_TESTS}</Row>
            {pipelineTests.map(test => (
                <Row nocols gap="s" key={test.id}>
                    <AmberField.checkbox model={testsModel(m => m[test.name])} label={test.name} />
                </Row>
            )) ?? LABELS.TESTS_NOT_CREATED}
        </AsyncContent>
    );
};

export default modelStoreExtention(TESTS_MODEL)(memo(PipelineTests));
