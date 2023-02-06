import React from 'react';
import {shallow} from 'enzyme';
import Article from '../Article';

describe('Components/article', () => {
    it('Если есть параметр theme - то применяется соответствующий класс', () => {
        const wrapper = shallow(<Article theme="test"/>);
        expect(wrapper.prop('className')).toContain('theme_test');
    });

    it('Прокидывает className на уровень компонента', () => {
        const wrapper = shallow(<Article className="test"/>);
        expect(wrapper.prop('className')).toContain('test');
    });

    it('Прокидываются дети внутрь компонента', () => {
        const wrapper = shallow(<Article><p id="test">test</p></Article>);
        expect(wrapper.find('#test').exists()).toBe(true);
    });
});
