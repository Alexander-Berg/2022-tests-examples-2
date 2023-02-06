import React from 'react';
import {mount, shallow} from 'enzyme';

import Input from '../Input';

describe('Components/input', () => {
    it('рендерит стандартный input', () => {
        const standardWrapper = mount(<Input/>);
        expect(standardWrapper.find('input').exists()).toBeTruthy();
    });

    it('Если есть параметр theme - то применяется соответствующий класс', () => {
        const wrapper = shallow(<Input theme="underline"/>);
        expect(wrapper.find('.amber-input_theme_underline').exists()).toBeTruthy();
    });

    it('Если есть параметр clear и есть значение, то показываем кнопку очистки', () => {
        const wrapper = shallow(<Input clear value="value"/>);
        expect(wrapper.find('.amber-input__clear').exists()).toBeTruthy();
    });

    it('Передача value', () => {
        const wrapper = mount(<Input value="test" clear/>);
        expect(wrapper.find('input[value="test"]').exists()).toBeTruthy();
    });

    it('onChange прокидывает значение', () => {
        const spy = jest.fn();

        const value = 'test';
        const myEvent = {target: {value}};
        const wrapper = mount(<Input onChange={spy}/>);
        wrapper.find('input').simulate('change', myEvent);

        expect(spy).toHaveBeenCalledWith(value);
    });

    it('needEvent прокидывает event при изменении', () => {
        const spy = jest.fn();

        const value = 'test';
        const myEvent = {target: {value}};
        const wrapper = mount(<Input needEvent onChange={spy}/>);
        wrapper.find('input').simulate('change', myEvent);

        expect(spy).toHaveBeenCalled();
        expect(spy.mock.calls[0][0].target.value).toEqual(value);
    });
});
