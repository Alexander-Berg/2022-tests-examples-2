import React, {memo} from 'react';
import {compose} from 'redux';

import AsyncContent from '_blocks/async-content';
import {SidePanel, SidePanelBody, SidePanelContent, SidePanelHeader} from '_blocks/side-panel';
import modal, {ModalProps} from '_hocs/modal';
import modelStoreExtension from '_hocs/model-store-extention';
import useService from '_hooks/use-service';
import HejmdalTestingResultModal from '_pkg/blocks/hejmdal-testing-result-modal';
import {HEJMDAL_TESTING_MODAL} from '_pkg/consts';

import {HEJMDAL_TESTING_MODEL, TEXTS} from './consts';
import HejmdalTestingForm from './HejmdalTestingForm';
import {service} from './service';
import {HejmdalModalLoadArgs} from './types';

type Props = Assign<ModalProps, HejmdalModalLoadArgs>;

function HejmdalTestingModal({schemaId, schemaJson, close, onDebug}: Props) {
    const {operationId} = useService(service, [schemaId]);

    return (
        <>
            <SidePanel width="l" onClose={close}>
                <SidePanelBody>
                    <AsyncContent id={operationId}>
                        <SidePanelHeader title={TEXTS.MODAL_TITLE} />
                        <SidePanelContent>
                            <HejmdalTestingForm schemaId={schemaId} schemaJson={schemaJson} onDebug={onDebug} />
                        </SidePanelContent>
                    </AsyncContent>
                </SidePanelBody>
            </SidePanel>
            <HejmdalTestingResultModal onDebug={onDebug} />
        </>
    );
}

export default compose(
    modelStoreExtension(HEJMDAL_TESTING_MODEL),
    modal(HEJMDAL_TESTING_MODAL),
    memo
)(HejmdalTestingModal);
