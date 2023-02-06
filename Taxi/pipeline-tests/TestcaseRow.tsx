import React, {FC, memo, useContext, useMemo} from 'react';

import JSONEditor from '_blocks/form/amber-field/code-editor/JSONEditor';
import {Panel, PanelGroupContext} from '_blocks/panel';
import {Col, Row} from '_blocks/row';
import {THEME} from '_pkg/consts';
import {prettyJSONStringify} from '_utils/prettyJSONStringify';

import {MAX_JS_CODE_ROWS, MIN_JS_CODE_ROWS} from '../../../common/consts';
import {LABELS} from '../../consts';
import {PipelineTestCaseResult} from '../../types';
import {Status} from './enums';

import {b} from './PipelineTests.styl';

type Props = {
    testcase: PipelineTestCaseResult;
};

const TestcaseRow: FC<Props> = ({testcase}) => {
    const {onToggle} = useContext(PanelGroupContext);

    const header = useMemo(
        () => (
            <Row gap="no">
                <Col>{LABELS.TESTCASE}</Col>
                <Col className={b('subname')}>{testcase.name}</Col>
            </Row>
        ),
        [testcase.name],
    );

    const testcaseStatus = testcase.passed ? Status.Success : Status.Error;

    const testcaseLogs = useMemo(() => testcase.logs ? prettyJSONStringify(testcase.logs) : undefined, [testcase.logs]);
    const testcaseErrorMessages = useMemo(() => testcase.error_message?.split('\n'), [testcase.error_message]);

    return (
        <Panel
            header={header}
            className={b('container')}
            activeKey={testcase.name}
            onToggle={onToggle}
            theme={THEME.WHITE}
            status={testcaseStatus}
        >
            {testcaseErrorMessages && (
                <Row nocols>
                    <Row gap="s">{LABELS.TESTCASE_ERRORS}:</Row>
                    {testcaseErrorMessages.map(message => (
                        <Row gap="s" className={b('error')}>
                            {message}
                        </Row>
                    ))}
                </Row>
            )}
            {testcase.failed_stage_names && (
                <Row>
                    <Row gap="s">{LABELS.OPTIONAL_STAGE_ERROS}:</Row>
                    <Row gap="s" className={b('error')}>
                        {testcase.failed_stage_names}
                    </Row>
                </Row>
            )}
            {testcaseLogs ? (
                <Row gap="l" nocols>
                    <Row>{LABELS.LOGS}:</Row>
                    <JSONEditor value={testcaseLogs} minLines={MIN_JS_CODE_ROWS} maxLines={MAX_JS_CODE_ROWS} readOnly />
                </Row>
            ) : (
                LABELS.LOGS_MISSING
            )}
        </Panel>
    );
};

export default memo(TestcaseRow);
