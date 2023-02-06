import React, {FC, Fragment, memo} from 'react';

import {FormMode, TabType} from '../../enums';
import {mockModel} from '../../utils';
import MockForm from '../mock-form';
import EntityBody from './EntityBody';
import EntityButtons from './EntityButtons';
import EntityHeader from './EntityHeader';

type Props = {
    tabType: TabType;
    mode: FormMode;
};

const MockContent: FC<Props> = ({tabType, mode}) => {
    return (
        <Fragment>
            <EntityHeader mode={mode} tabType={tabType} />
            <EntityBody mode={mode}>
                <MockForm model={mockModel(m => m)} mode={mode} />
            </EntityBody>
            <EntityButtons mode={mode} tabType={tabType} />
        </Fragment>
    );
};

export default memo(MockContent);
