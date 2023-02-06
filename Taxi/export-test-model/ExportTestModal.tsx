import Button from 'amber-blocks/button';
import {Modal, ModalContent} from 'amber-blocks/modal';
import React, {memo, useCallback} from 'react';
import {useSelector} from 'react-redux';

import {AmberField, Form} from '_blocks/form';
import {Col, Row} from '_blocks/row';
import modal, {ModalProps} from '_hocs/modal';
import useOperation from '_hooks/use-operation';
import useSaga from '_hooks/use-saga';
import {binded as commonActions} from '_infrastructure/actions';
import {useModelStoreExtention} from '_pkg/hooks/useModelStoreExtention';

import {EXPORT_TEST_MODAL, EXPORT_TEST_MODEL, ROOT_PATH, TABS} from '../../consts';
import {BundleState} from '../../types';
import {exportTestModel} from '../../utils';
import * as saga from './saga';

/* tslint:disable: jsx-literals-restriction*/

const handleClose = () => commonActions.modals.close(EXPORT_TEST_MODAL);

type Props = ModalProps & {
    exportRule?: string;
    exportTest?: string;
};

const ExportTestModal: React.FC<Props> = ({exportRule, exportTest}) => {
    useModelStoreExtention(EXPORT_TEST_MODEL);
    const {operationId} = useSaga(saga);
    const operation = useOperation({operationId});

    const exportToRule = useSelector((state: BundleState) => state[EXPORT_TEST_MODEL]?.ruleId);
    const rulesList = operation.result;
    const handleClick = useCallback(() => {
        handleClose();
        commonActions.router.pushWithQuery(`${ROOT_PATH}/view/${exportToRule}`, {
            view: TABS.TEST,
            importFrom: exportRule,
            testName: exportTest
        });
    }, [exportRule, exportTest, exportToRule]);
    return (
        <Modal onCloseRequest={handleClose}>
            <ModalContent>
                <h2>Экспорт теста</h2>
                <Form model={EXPORT_TEST_MODEL}>
                    <Row nocols>
                        <label>Наименование правила</label>
                    </Row>
                    <Row nocols>
                        <AmberField.select options={rulesList} model={exportTestModel(m => m.ruleId)} />
                    </Row>
                    <Row>
                        <Col>
                            <Button theme="accent" onClick={handleClick}>
                                Экспорт
                            </Button>
                        </Col>
                        <Col>
                            <Button onClick={handleClose}>Отмена</Button>
                        </Col>
                    </Row>
                </Form>
            </ModalContent>
        </Modal>
    );
};

export default modal(EXPORT_TEST_MODAL)(memo(ExportTestModal));
