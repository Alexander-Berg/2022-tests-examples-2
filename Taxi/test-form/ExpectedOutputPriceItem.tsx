import React, {memo, useMemo} from 'react';
import {useSelector} from 'react-redux';

import {AmberField, classNames} from '_blocks/form';
import {FormLayoutCol, FormLayoutRow} from '_blocks/form-layout';
import {getOperation} from '_infrastructure/selectors';

import {TESTING_MODEL} from '../../consts';
import TestingService from '../../sagas/services/TestingService';
import {BundleState} from '../../types';
import {testingModel} from '../../utils';

import {b} from './TestRuleForm.styl';

interface Props {
    item: keyof PricingDataPreparerDefinitionsYaml.CompositePrice;
}

const ExpectedOutputPriceItem: React.FC<Props> = ({item}) => {
    const operation = useSelector(getOperation(TestingService.runTest.id));
    const result = operation?.result;
    const showResult = useSelector((state: BundleState) => state[TESTING_MODEL]?.$meta?.showResult);
    const className = useMemo(
        () => (showResult && result?.output_price_lighting?.includes(item) ? b('highlight') : undefined),
        [item, showResult, result],
    );
    return (
        <FormLayoutRow className={className}>
            <FormLayoutCol>{item}</FormLayoutCol>
            <FormLayoutCol>
                <AmberField.text model={testingModel(m => m.output_price[item])} className={classNames.field100} />
            </FormLayoutCol>
        </FormLayoutRow>
    );
};

export default memo(ExpectedOutputPriceItem);
