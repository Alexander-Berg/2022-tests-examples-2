import moment from 'moment';
import React from 'react';

import {AmberField} from '_blocks/form';
import {FormLayoutGroup, FormLayoutSimple} from '_blocks/form-layout';
import i18n from '_utils/localization/i18n';

import {servicesModelPath} from '../../../utils/services';
import {ContractBlockProps} from '../service-block/types';

export interface TestCabinetConfigProps extends ContractBlockProps {}

const TestCabinetConfig = ({serviceSettings, serviceName}: TestCabinetConfigProps) => {
    const isTest = serviceSettings?.is_test;
    return (
        <FormLayoutGroup>
            <FormLayoutSimple label={i18n.print('test_cabinet')}>
                <AmberField.tumbler model={servicesModelPath(m => m.services[serviceName].is_test)} />
            </FormLayoutSimple>
            {isTest && (
                <React.Fragment>
                    <FormLayoutSimple label={i18n.print('disable_after_trips')}>
                        <AmberField.number
                            model={servicesModelPath(m => m.services[serviceName].deactivate_threshold_ride)}
                        />
                    </FormLayoutSimple>
                    <FormLayoutSimple label={i18n.print('disable,_date')}>
                        <AmberField.date
                            minDate={moment()}
                            model={servicesModelPath(m => m.services[serviceName].deactivate_threshold_date)}
                        />
                    </FormLayoutSimple>
                </React.Fragment>
            )}
        </FormLayoutGroup>
    );
};

export default TestCabinetConfig;
