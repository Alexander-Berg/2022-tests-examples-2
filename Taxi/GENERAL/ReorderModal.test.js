/* eslint-disable max-len */
import React from 'react';
import {ConfirmModal} from '@yandex-taxi/corp-core/modal';

import {shallow} from 'enzyme';
import {identity} from 'lodash';

import {ReorderModal} from './ReorderModal';

describe('ReorderModal', () => {
    it.only('не позволяет нажать кнопку заказа дважды, но разблокирует её после заказа', async () => {
        let promise;
        const onOKClick = jest.fn(() => (promise = Promise.resolve()));
        const onCancelRequest = jest.fn();
        const wrapper = shallow(
            <ReorderModal onOKClick={onOKClick} onCloseRequest={onCancelRequest} t={identity} />,
        );
        expect(wrapper).toMatchSnapshot();
        wrapper.find(ConfirmModal).prop('onOKClick')();
        expect(onOKClick).toHaveBeenCalled();
        expect(wrapper.state().inProgress).toBeTruthy();
        expect(wrapper.find(ConfirmModal).prop('OKDisabled')).toBe(true);
        await promise;
        expect(wrapper.find(ConfirmModal).prop('onOKClick')).not.toBeUndefined();
    });
});
