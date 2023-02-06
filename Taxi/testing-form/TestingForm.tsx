import React, {memo} from 'react';
import {useParams} from 'react-router';

import {TABS} from '../../consts';
import {useTypedQuery} from '../../hooks';
import DebugForm from '../debug-form';
import ExportTestModal from '../export-test-model';
import ImportFromOrderModal from '../import-from-order-modal';
import ImportTestModal from '../import-test-modal';
import SaveTemplateModal from '../save-template-modal';
import TestForm from '../test-form';
import TestList from '../test-list';

interface Props {
    isNew?: boolean;
}

const TestingForm: React.FC<Props> = ({isNew}) => {
    const {view: tab, testName} = useTypedQuery();
    const {id} = useParams<{id: string}>();
    if (isNew) {
        return (
            <>
                <DebugForm />
                <ImportFromOrderModal />
            </>
        );
    }
    return (
        <React.Fragment>
            {tab === TABS.DEBUG && <DebugForm/>}
            {tab === TABS.LIST && <TestList/>}
            {tab === TABS.TEST && <TestForm testName={testName} ruleId={id}/>}
            <ImportTestModal/>
            <ImportFromOrderModal/>
            <ExportTestModal/>
            <SaveTemplateModal/>
        </React.Fragment>
    );
};

export default memo(TestingForm);
