import Button from 'amber-blocks/button';
import React, {memo, useCallback} from 'react';
import {useParams} from 'react-router';

import {binded as commonActions} from '_infrastructure/actions';

import {IMPORT_TEST_MODAL, TABS} from '../../consts';
import {service} from '../../sagas/services/TestingService';

import {b} from './TestingFormButtons.styl';

/* tslint:disable: jsx-literals-restriction*/

const openImportModal = () => commonActions.modals.open(IMPORT_TEST_MODAL);

const goToNewTest = () => service.actions.changeTestingRoute({view: TABS.TEST});

const buttonClass = b('button');

const TestListButtons: React.FC = () => {
    const {id} = useParams<{id: string}>();
    const handleTest = useCallback(() => service.actions.runAllRuleTests(id), [id]);
    return (
        <React.Fragment>
            <Button className={buttonClass} onClick={handleTest} theme="accent">
                Запустить все тесты
            </Button>
            <Button className={buttonClass} onClick={goToNewTest}>
                Новый тест
            </Button>
            <Button className={buttonClass} onClick={openImportModal}>
                Импорт
            </Button>
        </React.Fragment>
    );
};

export default memo(TestListButtons);
