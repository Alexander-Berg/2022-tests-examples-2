import React, {FC, memo, useContext, useMemo} from 'react';

import {Panel, PanelGroup, PanelGroupContext} from '_blocks/panel';
import {Col, Row} from '_blocks/row';
import {THEME} from '_pkg/consts';
import {isNotEmpty} from '_utils/strict/validators';

import {LABELS} from '../../consts';
import {PipelineTestResult} from '../../types';
import {Status} from './enums';
import TestcaseRow from './TestcaseRow';

import {b} from './PipelineTests.styl';

type Props = {
    test: PipelineTestResult;
};

const TestRow: FC<Props> = ({test}) => {
    const {onToggle} = useContext(PanelGroupContext);

    const header = useMemo(
        () => (
            <Row gap="no">
                <Col>{LABELS.TEST}</Col>
                <Col className={b('subname')}>{test.name}</Col>
            </Row>
        ),
        [test.name],
    );

    const testStatus = useMemo(() => (test.testcases.some(t => !t.passed) ? Status.Error : Status.Success), [
        test.testcases,
    ]);

    return (
        <Panel header={header} activeKey={test.name} onToggle={onToggle} theme={THEME.WHITE} status={testStatus}>
            {isNotEmpty(test.testcases) ? (
                <PanelGroup multiSelect>
                    {test.testcases.map(testcase => (
                        <TestcaseRow testcase={testcase} key={testcase.name} />
                    ))}
                </PanelGroup>
            ) : (
                LABELS.TESTCASES_MISSING
            )}
        </Panel>
    );
};

export default memo(TestRow);
