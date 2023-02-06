import {shallow} from 'enzyme';
import React from 'react';
import Checkbox from '../Checkbox';

describe('Components/checkbox', () => {
    it('Передача атрибута disabled', () => {
        const wrapper = shallow(<Checkbox disabled label="Жми меня" />);
        expect(wrapper.find('input').prop('disabled')).toBeTruthy();
    });

    it('Передача атрибута checked', () => {
        const wrapper = shallow(<Checkbox checked label="Жми меня" />);
        expect(wrapper.find('input').prop('checked')).toBeTruthy();
    });

    it('Передача label', () => {
        const labelText = 'Жми меня';
        const wrapper = shallow(<Checkbox checked label={labelText} />);
        expect(wrapper.find('.amber-checkbox__content').length).toEqual(1);
        expect(wrapper.find('label').text()).toEqual(labelText);
    });

    it('Без label рисуется пустой лейбл', () => {
        const wrapper = shallow(<Checkbox checked />);
        expect(wrapper.find('.amber-checkbox__content').length).toEqual(1);
    });
});
