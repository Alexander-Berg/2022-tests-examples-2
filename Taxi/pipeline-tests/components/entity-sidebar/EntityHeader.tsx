import React, {FC, memo, useMemo} from 'react';

import {SidePanelHeader} from '_blocks/side-panel';

import {LABELS, SIDE_TITLES} from '../../consts';
import {FormMode, TabType} from '../../enums';

type Props = {
    tabType: TabType;
    mode: FormMode;
};

const EntityHeader: FC<Props> = ({tabType, mode}) => {
    const title = useMemo(() => SIDE_TITLES[tabType]?.[mode] ?? LABELS.MODE_NOT_SUPPORTED, [tabType, mode]);

    return (
        <SidePanelHeader title={title} />
    );
};

export default memo(EntityHeader);
