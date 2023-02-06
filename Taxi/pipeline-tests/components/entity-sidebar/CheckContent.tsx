import React, {FC, Fragment, memo} from 'react';

import {FormMode, TabType} from '../../enums';
import {checkModel} from '../../utils';
import CheckForm from '../check-form';
import EntityBody from './EntityBody';
import EntityButtons from './EntityButtons';
import EntityHeader from './EntityHeader';

type Props = {
    tabType: TabType;
    mode: FormMode;
};

const CheckContent: FC<Props> = ({tabType, mode}) => {
    return (
        <Fragment>
            <EntityHeader mode={mode} tabType={tabType} />
            <EntityBody mode={mode}>
                <CheckForm model={checkModel(m => m)} />
            </EntityBody>
            <EntityButtons mode={mode} tabType={tabType} />
        </Fragment>
    );
};

export default memo(CheckContent);
