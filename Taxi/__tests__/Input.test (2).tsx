import React from 'react';
import {shallow} from 'enzyme';
import Input from 'react-input-mask';

import InputMask from '../InputMask';

describe('Components/input-mask', () => {
    it('рендерит InputMask внутри InputMask', () => {
        const wrapper = shallow(<InputMask mask="99"/>);
        expect(wrapper.find(Input).exists()).toBeTruthy();
    });
});
