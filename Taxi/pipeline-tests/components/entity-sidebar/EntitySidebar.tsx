import React, {FC, memo} from 'react';

import AsyncContent from '_blocks/async-content';
import {SidePanel, SidePanelBody} from '_blocks/side-panel';
import {useQuery} from '_hooks/use-query-params';
import useSaga from '_hooks/use-saga';

import {FormMode, TabType} from '../../enums';
import {service as entityService} from '../../sagas/services/EntityService';
import {queryParsers} from '../../utils';
import TestContent from '../test-content';
import CheckContent from './CheckContent';
import MockContent from './MockContent';
import {saga} from './saga';

type Props = {
    tabType: TabType;
    mode: FormMode;
};

const handleClose = () => {
    entityService.actions.navigate({mode: undefined});
};

const EntitySidebar: FC<Props> = ({tabType, mode}) => {
    const {id} = useQuery(queryParsers);
    const {operationId} = useSaga(saga, [tabType, mode, id]);

    const isViewMode = mode === FormMode.View;

    return (
        <SidePanel width="m" onClose={handleClose} shouldCloseOnBackdropClick={isViewMode} backdrop={!isViewMode}>
            <SidePanelBody>
                <AsyncContent id={operationId}>
                    {tabType === TabType.Mock && <MockContent mode={mode} tabType={tabType} />}
                    {tabType === TabType.Check && <CheckContent mode={mode} tabType={tabType} />}
                    {tabType === TabType.Test && <TestContent mode={mode} tabType={tabType} />}
                </AsyncContent>
            </SidePanelBody>
        </SidePanel>
    );
};

export default memo(EntitySidebar);
