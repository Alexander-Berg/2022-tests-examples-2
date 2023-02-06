import React, {FC, Fragment, memo} from 'react';
import {compose} from 'redux';

import AsyncContent from '_blocks/async-content';
import modelStoreExtention from '_hocs/model-store-extention';
import useOperation from '_hooks/use-operation';
import useService from '_hooks/use-service';
import useToggle from '_hooks/use-toggle';
import {isNotEmpty} from '_utils/strict/validators';

import {FormMode, TabType, TestSubmode} from '../../enums';
import {testModel} from '../../utils';
import EntityBody from '../entity-sidebar/EntityBody';
import EntityButtons from '../entity-sidebar/EntityButtons';
import EntityHeader from '../entity-sidebar/EntityHeader';
import TestForm from '../test-form';
import {TEST_CHECK_EDIT_MODEL, TEST_MOCK_EDIT_MODEL} from './consts';
import TestContentService, {service as testContentService} from './sagas/TestContentService';
import SubmodeContent from './SubmodeContent';

type Props = {
    tabType: TabType;
    mode: FormMode;
};

const handleCloseSubmode = () => {
    testContentService.actions.closeSubmode();
};

const handleSetSubmode = (submode: TestSubmode, editIndex: number) => {
    testContentService.actions.setSubmode(submode, editIndex);
};

const TestContent: FC<Props> = ({tabType, mode}) => {
    const {submode, editIndex} = useOperation({operationId: TestContentService.setState.id!}).result ?? {};
    const {operationId} = useService(testContentService);

    const [hideContent, toggleContent] = useToggle(true);

    return (
        <AsyncContent id={operationId}>
            {!isNotEmpty(submode) && (
                <Fragment>
                    <EntityHeader mode={mode} tabType={tabType} />
                    <EntityBody mode={mode}>
                        <TestForm
                            model={testModel(m => m)}
                            hideContent={hideContent}
                            toggleContent={toggleContent}
                            onSetSubmode={handleSetSubmode}
                        />
                    </EntityBody>
                    <EntityButtons mode={mode} tabType={tabType} />
                </Fragment>
            )}
            {isNotEmpty(submode) && isNotEmpty(editIndex) && (
                <SubmodeContent
                    mode={mode}
                    submode={submode}
                    editIndex={editIndex}
                    onCloseSubmode={handleCloseSubmode}
                />
            )}
        </AsyncContent>
    );
};

export default compose(
    modelStoreExtention(TEST_CHECK_EDIT_MODEL),
    modelStoreExtention(TEST_MOCK_EDIT_MODEL),
    memo,
)(TestContent);
