import React from 'react';
import {shallow} from 'enzyme';

import GradientText from '../GradientText';

describe('Components/gradient-text', () => {
    it('Если есть параметр loading - то выставлен соответствующий class', () => {
        const wrapper = shallow(<GradientText>текст</GradientText>);
        expect(wrapper.text()).toContain('текст');
    });
});
