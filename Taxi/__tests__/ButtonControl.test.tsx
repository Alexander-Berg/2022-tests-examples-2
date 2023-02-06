import React from 'react';
import {shallow} from 'enzyme';

import {HTMLButtonProps} from '../../types';
import {OmitType} from '../../utils/typing';

import buttonControl, {ButtonControlProps} from '../buttonControl';

interface ButtonProps extends ButtonControlProps, OmitType<HTMLButtonProps, ButtonControlProps> {}

describe('Components/button-control', () => {
    it('возвращает то, что передали', () => {
        const Button = (props: HTMLButtonProps) => <button {...props}/>;
        const EnchancedButton = buttonControl<ButtonProps>(Button);

        const wrapper = shallow(<EnchancedButton theme="outline" size="l"/>);
        expect(wrapper.find(Button).exists()).toBeTruthy();
    });
});
