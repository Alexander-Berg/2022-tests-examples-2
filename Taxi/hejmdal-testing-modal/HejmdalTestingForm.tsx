import ButtonGroup from 'amber-blocks/button-group';
import React, {memo, useCallback} from 'react';
import {useSelector} from 'react-redux';

import AsyncButton from '_blocks/async-button';
import {Form} from '_blocks/form';
import {FormLayoutGroup} from '_blocks/form-layout';
import {Row} from '_blocks/row';
import useOperation from '_hooks/use-operation';

import {HEJMDAL_TESTING_MODEL, LOAD_TESTS_LIST, TEXTS} from './consts';
import HejmdalTestingTable from './HejmdalTestingTable';
import {getIsRunAllAvailable, getIsRunSelectedAvailable} from './selectors';
import HejmdalTestingService, {service} from './service';
import {HejmdalModalLoadArgs} from './types';
import {path} from './utils';

type Props = HejmdalModalLoadArgs;

export default memo<Props>(function HejmdalTestingForm({schemaId, schemaJson, onDebug}) {
    const {result} = useOperation({
        operationId: LOAD_TESTS_LIST
    });

    const handleRunAllTests = useCallback(() => {
        service.actions.runAllTests(schemaId, schemaJson);
    }, [schemaId, schemaJson]);

    const handleRunSelectedTests = useCallback(() => {
        service.actions.runSelectedTests(schemaId, schemaJson);
    }, [schemaId, schemaJson]);

    const handleRunTest = useCallback(
        (id: number) => {
            service.actions.runTest(schemaId, schemaJson, id);
        },
        [schemaId, schemaJson]
    );

    const isRunAllAvailable = useSelector(getIsRunAllAvailable);
    const isRunSelectedAvailable = useSelector(getIsRunSelectedAvailable);

    if (!result) {
        return null;
    }

    const hasEnabledTests = !!result.enabled.length;
    const hasDisabledTests = !!result.disabled.length;

    if (!hasEnabledTests && !hasDisabledTests) {
        return <p>{TEXTS.NO_TESTS}</p>;
    }

    return (
        <Form model={HEJMDAL_TESTING_MODEL}>
            <Row>
                <ButtonGroup>
                    <AsyncButton
                        id={HejmdalTestingService.runAllTests.id}
                        theme="accent"
                        children={TEXTS.RUN_ALL}
                        disabled={!isRunAllAvailable}
                        onClick={handleRunAllTests}
                    />
                    <AsyncButton
                        id={HejmdalTestingService.runSelectedTests.id}
                        theme="accent"
                        children={TEXTS.RUN_SELECTED}
                        disabled={!isRunSelectedAvailable}
                        onClick={handleRunSelectedTests}
                    />
                </ButtonGroup>
            </Row>
            {hasEnabledTests && (
                <FormLayoutGroup title={TEXTS.ENABLED_TESTS}>
                    <HejmdalTestingTable
                        items={result.enabled}
                        model={path(m => m.enabled)}
                        onRunTest={handleRunTest}
                        onDebug={onDebug}
                    />
                </FormLayoutGroup>
            )}
            {hasDisabledTests && (
                <FormLayoutGroup title={TEXTS.DISABLED_TESTS}>
                    <HejmdalTestingTable
                        items={result.disabled}
                        model={path(m => m.disabled)}
                        onRunTest={handleRunTest}
                        onDebug={onDebug}
                    />
                </FormLayoutGroup>
            )}
        </Form>
    );
});
