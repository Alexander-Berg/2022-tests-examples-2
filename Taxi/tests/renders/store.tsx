import React, {ReactNode} from 'react';
import {Provider} from 'react-redux';

import appStore from 'reduxStore';

export function createStoreProvider(children: ReactNode) {
    return (
        <Provider store={appStore}>
            {children}
        </Provider>
    );
}
