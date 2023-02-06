import React from 'react';
import {mount} from 'enzyme';

import Textarea from '../Textarea';

describe('Components/textarea', () => {
    it('рендерит textarea', () => {
        const wrapper = mount(<Textarea/>);
        expect(wrapper.find('textarea').exists()).toBeTruthy();
    });
});
