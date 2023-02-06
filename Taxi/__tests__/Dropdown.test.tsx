import React from 'react';
import {shallow} from 'enzyme';

import Button from '../../button/Button';
import Dropdown, {DropdownProps, DropdownState} from '../Dropdown';

describe('Components/dropdown', () => {
    it('Обработка клика на Dropdown', () => {
        const onOpen = jest.fn();
        const onClose = jest.fn();
        const wrapper = shallow<Dropdown, DropdownProps, DropdownState>(
            <Dropdown controlComponent={<Button />} onOpen={onOpen} onClose={onClose}/>
        );

        wrapper.find(Button).simulate('click');
        expect(wrapper.state().isOpen).toBeTruthy();
        expect(onOpen).toHaveBeenCalledTimes(1);
        wrapper.find(Button).simulate('click');
        expect(wrapper.state().isOpen).toBeFalsy();
        expect(onOpen).toHaveBeenCalledTimes(1);
        expect(onClose).toHaveBeenCalledTimes(1);
    });
});
