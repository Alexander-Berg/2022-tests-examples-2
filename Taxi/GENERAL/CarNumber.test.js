import React from 'react';
import {shallow} from 'enzyme';
import CarNumber from './CarNumber';

describe('Blocks/CarNumber', () => {
    it('Российский номер рендерится в разметку', () => {
        let wrapper = shallow(<CarNumber number="s302EE99"/>);

        expect(wrapper.hasClass('CarNumber_type_rus')).toBe(true);
        expect(wrapper.find('sup').text()).toBe('99');
    });

    it('Жёлтый номер рендерится в разметку', () => {
        let wrapper = shallow(<CarNumber number="md3029"/>);

        expect(wrapper.hasClass('CarNumber_type_rus-yellow')).toBe(true);
        expect(wrapper.find('sup').text()).toBe('9');
    });

    it('Неизвестный номер рендерится без изменений', () => {
        let wrapper = shallow(<CarNumber number="XXX123"/>);
        expect(wrapper.find('sup').exists()).toBe(false);
    });

    it('classname добавляется', () => {
        let wrapper = shallow(<CarNumber number="text" className="test"/>);
        expect(wrapper.hasClass('test')).toBe(true);
    });
});
