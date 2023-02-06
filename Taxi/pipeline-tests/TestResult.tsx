import moment from 'moment';
import React, {FC, memo, useMemo} from 'react';

import {classNames} from '_blocks/form';
import {PanelGroup} from '_blocks/panel';
import {Row} from '_blocks/row';

import {DATE_FORMAT, LABELS} from '../../consts';
import {PipelineTestsResults} from '../../types';
import TestRow from './TestRow';

import {b} from './PipelineTests.styl';

type Props = {
    result: PipelineTestsResults;
};

const TestResult: FC<Props> = ({result}) => {
    const startTime = useMemo(() => `${LABELS.START_TIME}: ${moment(result.created).format(DATE_FORMAT)}`, [
        result.created,
    ]);

    return (
        <Row gap="l" nocols>
            <Row className={b('title')}>{LABELS.TEST_RESULTS}</Row>
            <Row className={classNames.labelGray}>{startTime}</Row>
            <PanelGroup multiSelect>
                {result.tests.map(test => (
                    <TestRow test={test} key={test.name} />
                ))}
            </PanelGroup>
        </Row>
    );
};

export default memo(TestResult);
