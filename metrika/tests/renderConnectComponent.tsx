import * as React from 'react';
import { Provider, InferableComponentEnhancerWithProps } from 'react-redux';
import { mount } from 'enzyme';

import { Store } from 'redux';

const MockComponent = function <P>(_props: P) {
    return null;
};

export const renderConnectComponent = function <P>(
    connector: InferableComponentEnhancerWithProps<P, {}>,
    store: Store,
) {
    const ConnectedComponent = connector(MockComponent);
    const wrapped = mount(
        <Provider store={store}>
            <ConnectedComponent />
        </Provider>,
    );
    const getElement = () => {
        wrapped.update();
        return wrapped.find<P>(MockComponent);
    };
    return { store, getElement };
};
