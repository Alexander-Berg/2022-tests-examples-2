import React from 'react';
import {shallow} from 'enzyme';

import {HTMLInputProps} from '../../types';
import {OmitType} from '../../utils/typing';

import inputControl, {InputControlProps} from '../inputControl';

interface InputProps extends InputControlProps, OmitType<HTMLInputProps, InputControlProps> {}

describe('Components/input-control', () => {
    it('возвращает то, что передали', () => {
        const Input = (props: HTMLInputProps) => <input {...props}/>;
        const EnchancedInput = inputControl<InputProps>(Input);

        const wrapper = shallow(<EnchancedInput theme="outline" size="l"/>);
        expect(wrapper.find(Input).exists()).toBeTruthy();
    });
});
