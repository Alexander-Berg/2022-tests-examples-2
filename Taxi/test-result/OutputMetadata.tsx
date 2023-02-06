import React, {memo, useMemo} from 'react';
import {useSelector} from 'react-redux';

import {AmberTr} from '_blocks/amber-table';

import {TestRuleResponse} from '../../api/types';
import {TESTING_MODEL} from '../../consts';
import {BundleState} from '../../types';

import {b} from './TestResult.styl';

interface Props {
    item: string;
    data: TestRuleResponse;
}

const OutputMetadata: React.FC<Props> = ({data, item}) => {
    const metadata = useSelector((state: BundleState) => state[TESTING_MODEL].output_meta);
    const className = useMemo(
        () =>
            data.metadata_lighting?.includes(item)
                ? b('highlight', {
                      yellow: !metadata?.some(meta => meta.key === item),
                  })
                : undefined,
        [metadata, data, item],
    );
    return (
        <AmberTr className={className}>
            <td>{item}</td>
            <td>{data.metadata_map?.[item]}</td>
        </AmberTr>
    );
};

export default memo(OutputMetadata);
