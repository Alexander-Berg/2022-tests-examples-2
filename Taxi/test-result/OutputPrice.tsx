import React, {memo, useMemo} from 'react';

import {FormLayoutCol, FormLayoutRow} from '_blocks/form-layout';

import {TestRuleResponse} from '../../api/types';
import {CompositePrice} from '../../types';

import {b} from './TestResult.styl';

interface Props {
    item: keyof CompositePrice;
    data: TestRuleResponse;
}

const OutputPrice: React.FC<Props> = ({item, data}) => {
    const className = useMemo(() => (data.output_price_lighting?.includes(item) ? b('highlight') : undefined), [data]);
    return (
        <FormLayoutRow className={className}>
            <FormLayoutCol>{item}</FormLayoutCol>
            <FormLayoutCol>{data.output_price?.[item]}</FormLayoutCol>
        </FormLayoutRow>
    );
};

export default memo(OutputPrice);
