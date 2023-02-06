import {Button, ButtonGroup} from 'amber-blocks';
import React, {FC, memo, useCallback} from 'react';

import {SidePanelFooter} from '_blocks/side-panel';
import {useQuery} from '_hooks/use-query-params';
import {THEME} from '_pkg/consts';

import {LABELS} from '../../consts';
import {FormMode, TabType} from '../../enums';
import {service as entityService} from '../../sagas/services/EntityService';
import {queryParsers} from '../../utils';

type Props = {
    tabType: TabType;
    mode: FormMode;
};

const handleClose = () => {
    entityService.actions.navigate({mode: undefined});
};

const handleEdit = () => {
    entityService.actions.navigate({mode: FormMode.Edit});
};

const EntityButtons: FC<Props> = ({tabType, mode}) => {
    const {id} = useQuery(queryParsers);

    const handleSaveEntity = useCallback(() => {
        entityService.actions.saveEntity(tabType);
    }, [tabType]);

    const handleEditEntity = useCallback(() => {
        if (id) {
            entityService.actions.editEntity(tabType, id);
        }
    }, [tabType, id]);

    return (
        <SidePanelFooter>
            <ButtonGroup>
                {mode === FormMode.Create && (
                    <Button theme={THEME.ACCENT} onClick={handleSaveEntity}>
                        {LABELS.CREATE}
                    </Button>
                )}
                {mode === FormMode.View && <Button onClick={handleEdit}>{LABELS.EDIT}</Button>}
                {mode === FormMode.Edit && (
                    <Button theme={THEME.ACCENT} onClick={handleEditEntity}>
                        {LABELS.SAVE_CHANGES}
                    </Button>
                )}
                <Button onClick={handleClose}>{LABELS.CANCEL}</Button>
            </ButtonGroup>
        </SidePanelFooter>
    );
};

export default memo(EntityButtons);
