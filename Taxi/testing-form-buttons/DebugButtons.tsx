import Button from 'amber-blocks/button';
import isEmpty from 'lodash/isEmpty';
import React, {memo, useCallback} from 'react';
import {useSelector} from 'react-redux';

import PermissionButton from '_blocks/button-permission';
import {Col, Row} from '_blocks/row';

import {binded as actions} from '../../actions';
import {MODEL} from '../../consts';
import {useTypedQuery} from '../../hooks';
import {service} from '../../sagas/services/TestingService';
import {BundleState} from '../../types';

/* tslint:disable: jsx-literals-restriction*/

const DebugButtons: React.FC = () => {
    const sourceCode = useSelector((state: BundleState) => state[MODEL].source_code);
    const {view} = useTypedQuery();
    const handleImport = useCallback(() => {
        service.actions.openImportModal(view);
    }, [view]);
    return (
        <Row>
            <Col>
                <PermissionButton
                    onClick={actions.rulesService.testRule}
                    theme="accent"
                    disabled={isEmpty(sourceCode)}
                >
                    Тестировать
                </PermissionButton>
            </Col>
            <Col>
                <Button onClick={handleImport}>Импорт из заказа</Button>
            </Col>
        </Row>
    );
};

export default memo(DebugButtons);
