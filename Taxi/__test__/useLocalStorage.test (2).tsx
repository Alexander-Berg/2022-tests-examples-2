import {mount} from 'enzyme';
import React from 'react';
import {Provider} from 'react-redux';

import store from '_pkg/infrastructure/store';
import {PersistentKey} from '_types/common/infrastructure';

import {useLocalStorage} from '../use-local-storage';

type Settings = {
    col1: boolean;
};

const KEY = 'key' as PersistentKey<Settings>;

const ConsumerComponent: React.FC<{}> = () => {
    const [value] = useLocalStorage(KEY);

    return (
        <span id="consumer">
            {JSON.stringify(value)}
        </span>
    );
};

const ProviderComponent: React.FC<{}> = () => {
    const [, setValue] = useLocalStorage(KEY);

    const onClick = () => setValue({
        col1: true
    });

    return (
        <button
            id="provider"
            onClick={onClick}
        />
    );
};

const Root: React.FC<{}> = () => (
    <Provider store={store}>
        <ProviderComponent/>
        <ConsumerComponent/>
    </Provider>
);

describe('useLocalStorage', () => {
    beforeEach(() => {
        localStorage.clear();
    });

    test('Get value', () => {
        const wrapper = mount(<Root/>);

        expect(wrapper.find('#consumer').getDOMNode().innerHTML).toBe('');

        wrapper.unmount();
    });

    test('Set value', () => {
        const wrapper = mount(<Root/>);

        wrapper.find('#provider').simulate('click');
        expect(JSON.parse(wrapper.find('#consumer').getDOMNode().innerHTML)).toStrictEqual({col1: true});

        wrapper.unmount();
    });
});
