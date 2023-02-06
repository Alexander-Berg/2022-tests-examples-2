import React, {FC, memo, PropsWithChildren} from 'react';

import {SidePanelContent} from '_blocks/side-panel';
import {IsFormDisabled} from '_contexts/is-form-disabled';

import {FormMode} from '../../enums';

type Props = PropsWithChildren<{
    mode: FormMode;
}>;

const EntityBody: FC<Props> = ({mode, children}) => {
    const disabled = mode === FormMode.View || !Object.values(FormMode).includes(mode);

    return (
        <SidePanelContent>
            <IsFormDisabled.Provider value={disabled}>
                {children}
            </IsFormDisabled.Provider>
        </SidePanelContent>
    );
};

export default memo(EntityBody);
