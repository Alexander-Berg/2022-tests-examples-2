import React from 'react';
import {shallow} from 'enzyme';
import Nav from '../Nav';

describe('Components/Nav', () => {
    it('По дефолту есть имя класса amber-nav', () => {
        const wrapper = shallow(<Nav />);
        expect(wrapper.prop('className')).toContain('amber-nav');
    });
    it('Если есть параметр className - то применяется соответствующий класс', () => {
        const customClassName = 'customClass';
        const wrapper = shallow(
            <Nav className={customClassName}/>
        );
        expect(wrapper.prop('className')).toContain(customClassName);
    });
});
