import {concat} from 'lodash';
import React, {FC, Fragment, memo, useMemo} from 'react';

import {AmberField} from '_blocks/form';
import {Props as AsyncSelectProps} from '_blocks/form/amber-field/async-select/types';
import useOperation from '_hooks/use-operation';
import useSaga from '_hooks/use-saga';
import useStrictModel from '_hooks/use-strict-model';
import {binded as commonActions} from '_infrastructure/actions';
import ValidationErrors from '_pkg/blocks/validation-errors';
import {StrictModel} from '_types/common/infrastructure';
import {stringToOption} from '_utils/stringToOption';

import {TestCheckModel} from '../../types';
import {saga} from './saga';

type Props = Omit<AsyncSelectProps, 'model' | 'loadId' | 'options'> & {
    model: StrictModel<string[]>;
    checks: TestCheckModel[];
};

const ChecksSelect: FC<Props> = ({checks, ...props}) => {
    const selectValues = useStrictModel(props.model);

    const {operationId} = useSaga(saga);
    const {result} = useOperation({operationId});

    const options = useMemo(() => {
        return concat(
            (result?.output_checks ?? []).map(check => stringToOption(check.name)),
            checks.map(check => ({
                label: check.checkName,
                value: check._id,
            })),
        );
    }, [result, checks]);

    const filteredSelectedValues = useMemo(
        () => selectValues.filter(value => options.some(opt => opt.value === value)),
        [options, selectValues],
    );

    if (result && filteredSelectedValues.length !== selectValues.length) {
        commonActions.form.strict.change(props.model, filteredSelectedValues);
    }

    return (
        <Fragment>
            <AmberField.asyncSelect {...props} loadId={operationId} options={options} />
            <ValidationErrors model={props.model} />
        </Fragment>
    );
};

export default memo(ChecksSelect);
