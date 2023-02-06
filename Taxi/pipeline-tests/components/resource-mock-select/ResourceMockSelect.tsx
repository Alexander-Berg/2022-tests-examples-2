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
import {isNotEmpty} from '_utils/strict/validators';
import {stringToOption} from '_utils/stringToOption';

import {TestMockModel} from '../../types';
import {saga} from './saga';

type Props = Omit<AsyncSelectProps, 'model' | 'loadId' | 'options'> & {
    model: StrictModel<string>;
    resource: string;
    mocks: TestMockModel[];
};

const filterMocks = <T extends {resource?: string}>(items: T[], resource: string): T[] => {
    return items.filter(item => isNotEmpty(resource) && item.resource === resource);
};

const ResourceMockSelect: FC<Props> = ({resource, mocks, ...props}) => {
    const {operationId} = useSaga(saga);
    const selectValue = useStrictModel(props.model);
    const {result} = useOperation({operationId});

    const options = useMemo(() => {
        const apiMocks = filterMocks(
            concat(result?.resources_mocks ?? [], result?.prefetched_resources_mocks ?? []),
            resource,
        );
        const innerMocks = filterMocks(mocks, resource);

        return concat(
            apiMocks.map(mock => stringToOption(mock.name)),
            innerMocks.map(mock => ({
                label: mock.mockName,
                value: mock._id,
            })),
        );
    }, [result, resource, mocks]);

    if (result && options.every(({value}) => value !== selectValue)) {
        commonActions.form.strict.change(props.model, '');
    }

    return (
        <Fragment>
            <AmberField.asyncSelect {...props} loadId={operationId} options={options} />
            <ValidationErrors model={props.model} />
        </Fragment>
    );
};

export default memo(ResourceMockSelect);
