import Button from 'amber-blocks/button';
import {Modal, ModalContent} from 'amber-blocks/modal';
import {IRadioButtonOption} from 'amber-blocks/radio-button/types';
import React, {memo, useMemo} from 'react';
import {useSelector} from 'react-redux';

import {AmberField, Form} from '_blocks/form';
import JSONEditorField from '_blocks/form/amber-field/code-editor/JSONEditorField';
import {Col, Row} from '_blocks/row';
import modal from '_hocs/modal';
import useOperation from '_hooks/use-operation';
import useSaga from '_hooks/use-saga';
import {binded as commonActions} from '_infrastructure/actions';
import Box from '_pkg/blocks/box';
import {useModelStoreExtention} from '_pkg/hooks/useModelStoreExtention';
import {arrayOfStringToOptions} from '_utils/stringToOption';

import {IMPORT_TEST_MODAL, IMPORT_TEST_MODEL} from '../../consts';
import {GET_ALL_TESTS_ID, service as testingService} from '../../sagas/services/TestingService';
import {BundleState, ImportTestModelType} from '../../types';
import {importTestModel} from '../../utils';
import * as saga from './saga';

import {b} from './ImportTestModal.styl';

/* tslint:disable: jsx-literals-restriction*/

const handleClose = () => commonActions.modals.close(IMPORT_TEST_MODAL);

const handleClick = () => testingService.actions.importTest();

const options: IRadioButtonOption<ImportTestModelType>[] = [
    {label: 'Из библиотеки', value: ImportTestModelType.Default},
    {label: 'Из JSON', value: ImportTestModelType.Json},
];

const ImportTestModal: React.FC = () => {
    useModelStoreExtention(IMPORT_TEST_MODEL);

    useSaga(saga);
    const allTests = useOperation({operationId: GET_ALL_TESTS_ID}).result;

    const ruleOptions = useMemo(() => {
        const ruleNames = Object.keys(allTests || {});
        return arrayOfStringToOptions(ruleNames);
    }, [allTests]);

    const [tab, importRule] = useSelector((state: BundleState) => [
        state[IMPORT_TEST_MODEL]?.tab ?? ImportTestModelType.Default,
        state[IMPORT_TEST_MODEL]?.ruleName,
    ]);

    const testOptions = useMemo(() => {
        const tests = importRule ? allTests?.[importRule]?.tests : [];
        return arrayOfStringToOptions(tests);
    }, [importRule, allTests]);

    return (
        <Modal onCloseRequest={handleClose} className={b()}>
            <ModalContent>
                <h2>Импорт теста</h2>
                <Form model={IMPORT_TEST_MODEL} className={b('content')}>
                    <Box mb={2}>
                        <AmberField.radioButton
                            model={importTestModel(m => m.tab)}
                            options={options}
                            defaultValue={ImportTestModelType.Default}
                        />
                    </Box>
                    {tab === ImportTestModelType.Default && (
                        <>
                            <Row nocols>
                                <label>Наименование правила или библиотеки</label>
                            </Row>
                            <Row nocols>
                                <AmberField.select options={ruleOptions} model={importTestModel(m => m.ruleName)} />
                            </Row>
                            <Row nocols>
                                <label>Наименование теста</label>
                            </Row>
                            <Row nocols>
                                <AmberField.select options={testOptions} model={importTestModel(m => m.testName)} />
                            </Row>
                        </>
                    )}
                    {tab === ImportTestModelType.Json && (
                        <Box mb={2} display="block">
                            <JSONEditorField model={importTestModel(m => m.json)} placeholder="JSON" />
                        </Box>
                    )}
                </Form>
                <Row className={b('actionButtons')}>
                    <Col>
                        <Button theme="accent" onClick={handleClick}>
                            Импорт
                        </Button>
                    </Col>
                    <Col>
                        <Button onClick={handleClose}>Отмена</Button>
                    </Col>
                </Row>
            </ModalContent>
        </Modal>
    );
};

export default modal(IMPORT_TEST_MODAL)(memo(ImportTestModal));
