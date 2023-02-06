import Button from 'amber-blocks/button';
import Dropdown from 'amber-blocks/dropdown/Dropdown';
import {Item, ItemCol, List} from 'amber-blocks/list';
import React, {memo, useCallback} from 'react';
import {useSelector} from 'react-redux';
import {useParams} from 'react-router-dom';

import {binded as commonActions} from '_infrastructure/actions';

import {EXPORT_TEST_MODAL, IMPORT_TEST_MODAL, SAVE_TEMPLATE_MODAL, TESTING_MODEL} from '../../consts';
import {useTypedQuery} from '../../hooks';
import {service as testingService} from '../../sagas/services/TestingService';
import {BundleState} from '../../types';

import {b} from './TestingFormButtons.styl';

/* tslint:disable: jsx-literals-restriction*/

const handleImport = () => commonActions.modals.open(IMPORT_TEST_MODAL);
const handleSaveTemplate = () => commonActions.modals.open(SAVE_TEMPLATE_MODAL);
const handleCopyTestAsJson = () => testingService.actions.copyTestAsJsonToClipboard();

const TestButtons: React.FC = () => {
    const {testName, importFrom, view} = useTypedQuery();
    const {id: ruleId} = useParams<{id: string}>();
    const isEdit = testName !== undefined;
    const isImport = importFrom !== undefined;
    const handleDelete = useCallback(() => {
        if (testName) {
            testingService.actions.deleteTest(ruleId, testName);
        }
    }, [ruleId, testName]);
    const name = useSelector((state: BundleState) => state[TESTING_MODEL].name);
    const handleExport = useCallback(() =>
        commonActions.modals.open(EXPORT_TEST_MODAL, {exportRule: ruleId, exportTest: testName}), [ruleId, testName]
    );
    const handleCopy = useCallback(() =>
        testingService.actions.changeTestingRoute({
            view,
            testName,
            importFrom: ruleId
        }), [ruleId, testName]
    );
    const handleImportFromOrder = useCallback(() => {
        if (view) {
            testingService.actions.openImportModal(view);
        }
    }, [view]);

    return (
        <React.Fragment>
            <Button
                className={b('button')}
                theme="accent"
                onClick={isEdit ? testingService.actions.editTest : testingService.actions.saveNewTest}
            >
                Сохранить
            </Button>
            {isEdit && (
                <Button className={b('button')} theme="color" onClick={handleDelete}>
                    Удалить
                </Button>
            )}
            <Button className={b('button')} onClick={testingService.actions.runTest} disabled={!name}>
                Тестировать
            </Button>
            <Dropdown controlComponent={<Button className={b('button')}>Действия...</Button>}>
                <List>
                    {isEdit && !isImport && (
                        <Item onClick={handleCopy}>
                            <ItemCol>Копировать</ItemCol>
                        </Item>
                    )}
                    <Item onClick={handleImport}>
                        <ItemCol>Импорт</ItemCol>
                    </Item>
                    <Item onClick={handleImportFromOrder}>
                        <ItemCol>Импорт из заказа</ItemCol>
                    </Item>
                    {isEdit && !isImport && (
                        <Item onClick={handleExport}>
                            <ItemCol>Экспорт</ItemCol>
                        </Item>
                    )}
                    <Item onClick={handleCopyTestAsJson}>
                        <ItemCol>Скопировать JSON теста</ItemCol>
                    </Item>
                    <Item onClick={handleSaveTemplate}>
                        <ItemCol>Сохранить как шаблон</ItemCol>
                    </Item>
                </List>
            </Dropdown>
        </React.Fragment>
    );
};

export default memo(TestButtons);
