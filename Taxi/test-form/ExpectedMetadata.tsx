import cn from 'classnames';
import React, {memo, useMemo} from 'react';
import {useSelector} from 'react-redux';

import {AmberField} from '_blocks/form';
import {getOperation} from '_infrastructure/selectors';
import model from '_utils/model';

import {TESTING_MODEL} from '../../consts';
import TestingService from '../../sagas/services/TestingService';
import {BundleState} from '../../types';

import {b} from './TestRuleForm.styl';

interface Metadata {
    key: string;
    value: string;
}

interface Props {
    metadata: Metadata;
    model: string;
    index: number;
}

const metadataModel = (path: (m: Metadata[]) => unknown) => model(path);

const ExpectedMetadata: React.FC<Props> = ({metadata, model, index}) => {
    const operation = useSelector(getOperation(TestingService.runTest.id));
    const showResult = useSelector((state: BundleState) => state[TESTING_MODEL]?.$meta?.showResult);
    const result = operation?.result;
    const highlightClass = useMemo(
        () =>
            showResult &&
            result?.metadata_lighting?.includes(metadata.key) &&
            b('highlight', {yellow: !result?.metadata_map?.[metadata.key]}),
        [showResult, metadata.key, result]
    );
    return (
        <div className={cn(highlightClass, b('metadata'))}>
            <AmberField.text placeholder="key" model={`${model}${metadataModel(m => m[index].key)}`} />
            <AmberField.number placeholder="value" model={`${model}${metadataModel(m => m[index].value)}`} />
        </div>
    );
};

export default memo(ExpectedMetadata);
