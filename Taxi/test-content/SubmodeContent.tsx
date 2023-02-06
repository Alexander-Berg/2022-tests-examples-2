import {Button, ButtonGroup} from 'amber-blocks';
import React, {FC, memo, useCallback, useMemo} from 'react';

import AsyncContent from '_blocks/async-content';
import {SidePanelContent, SidePanelFooter, SidePanelHeader} from '_blocks/side-panel';
import {IsFormDisabled} from '_contexts/is-form-disabled';
import useSaga from '_hooks/use-saga';
import useStrictModel from '_hooks/use-strict-model';
import {THEME} from '_pkg/consts';
import {isEmpty} from '_utils/strict/validators';

import {LABELS} from '../../consts';
import {FormMode, TestSubmode} from '../../enums';
import CheckForm from '../check-form';
import MockForm from '../mock-form';
import {SUBMODE_EDIT_HEADERS} from './consts';
import {saga} from './sagas/saga';
import {service as testContentService} from './sagas/TestContentService';
import {testCheckModel, testMockModel} from './utils';

type Props = {
    mode: FormMode;
    submode: TestSubmode;
    editIndex: number;
    onCloseSubmode: () => void;
};

const SubmodeContent: FC<Props> = ({mode, submode, editIndex, onCloseSubmode}) => {
    const {operationId} = useSaga(saga, [submode, editIndex]);

    const disabled = useMemo(() => mode === FormMode.View, [mode]);

    const mockId = useStrictModel(testMockModel(m => m._id));
    const checkId = useStrictModel(testCheckModel(m => m._id));

    const title = useMemo(() => {
        if (isEmpty(mockId) && submode === TestSubmode.MockEdit) {
            return LABELS.CREATE_TEST_MOCK;
        } else if (isEmpty(checkId) && submode === TestSubmode.CheckEdit) {
            return LABELS.CREATE_TEST_CHECK;
        }

        return SUBMODE_EDIT_HEADERS[submode];
    }, [submode, mockId, checkId]);

    const handleSaveSubEntity = useCallback(() => {
        if (submode === TestSubmode.CheckEdit) {
            testContentService.actions.saveCheck(editIndex);
        } else if (submode === TestSubmode.MockEdit) {
            testContentService.actions.saveMock(editIndex);
        }
    }, [submode, editIndex]);

    return (
        <AsyncContent id={operationId}>
            <SidePanelHeader title={title} />
            <SidePanelContent>
                <IsFormDisabled.Provider value={disabled}>
                    {submode === TestSubmode.MockEdit && <MockForm model={testMockModel(m => m)} />}
                    {submode === TestSubmode.CheckEdit && <CheckForm model={testCheckModel(m => m)} />}
                </IsFormDisabled.Provider>
            </SidePanelContent>
            <SidePanelFooter>
                <ButtonGroup>
                    {!disabled && (
                        <Button theme={THEME.ACCENT} onClick={handleSaveSubEntity}>
                            {LABELS.SAVE}
                        </Button>
                    )}
                    <Button onClick={onCloseSubmode}>{LABELS.CANCEL}</Button>
                </ButtonGroup>
            </SidePanelFooter>
        </AsyncContent>
    );
};

export default memo(SubmodeContent);
