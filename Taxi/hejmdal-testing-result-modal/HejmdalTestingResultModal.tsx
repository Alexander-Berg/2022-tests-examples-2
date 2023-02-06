import Button from 'amber-blocks/button';
import {Modal, ModalContent, ModalTitle} from 'amber-blocks/modal';
import Section from 'amber-blocks/section';
import {groupBy} from 'lodash';
import React, {memo, useMemo} from 'react';
import {compose} from 'redux';

import Alert from '_blocks/alert';
import {FormLayoutGroup} from '_blocks/form-layout';
import modal, {ModalProps} from '_hocs/modal';
import {HEJMDAL_TESTING_RESULT_MODAL} from '_pkg/consts';

import {TEXTS} from './consts';
import HejmdalTestingResultTable from './HejmdalTestingResultTable';
import {TestsResponse} from './types';

type Props = Assign<
    ModalProps,
    {
        response: TestsResponse;
        onDebug: (id: number) => void;
    }
>;

function HejmdalTestingResultModal({response, onDebug, close}: Props) {
    const {error_message, test_case_results} = response;

    const tests = useMemo(() => groupBy(test_case_results, x => !!x.enabled), [test_case_results]);

    return (
        <Modal onCloseRequest={close}>
            <ModalContent size="l" padding={null}>
                <ModalTitle>{TEXTS.MODAL_TITLE}</ModalTitle>
                {error_message && <Alert type="error">{error_message}</Alert>}
                <Section scrollable>
                    {!!tests.true?.length && (
                        <FormLayoutGroup title={TEXTS.ENABLED_TESTS}>
                            <HejmdalTestingResultTable tests={tests.true} onDebug={onDebug} />
                        </FormLayoutGroup>
                    )}
                    {!!tests.false?.length && (
                        <FormLayoutGroup title={TEXTS.DISABLED_TESTS}>
                            <HejmdalTestingResultTable tests={tests.false} onDebug={onDebug} />
                        </FormLayoutGroup>
                    )}
                </Section>
                <Section theme="gray">
                    <Button theme="accent" children={TEXTS.OK} onClick={close} />
                </Section>
            </ModalContent>
        </Modal>
    );
}

export default compose(modal(HEJMDAL_TESTING_RESULT_MODAL), memo)(HejmdalTestingResultModal);
