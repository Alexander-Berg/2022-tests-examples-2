import React from 'react';
import {shallow} from 'enzyme';

import RadioButton from '../RadioButton';
import RadioItem from '../item';

const options = [
    {label: 'Пункт 1', value: 1},
    {label: 'Пункт 2', value: 2},
    {label: 'Пункт 3', value: 3, disabled: true},
    {label: 'Пункт 4', value: 4, disabled: true}
];

const currentValue = 4;

describe('Components/radio', () => {
    it('Передача options', () => {
        const wrapper = shallow(<RadioButton options={options} name="radio" />);

        expect(wrapper.find(RadioItem).length).toEqual(options.length);
    });

    it('Передача текущего значения', () => {
        const wrapper = shallow(<RadioButton options={options} value={currentValue} name="radio" />);

        const checked = wrapper.find(RadioItem).findWhere(option => {
            return option.dive().find('.amber-radio-button__radio_checked').length > 0;
        });

        expect(checked.exists()).toBeTruthy();
        expect(checked.prop('value')).toEqual(currentValue);
    });

    it('Отображение компонента с ошибкой', () => {
        const wrapper = shallow(<RadioButton options={options} value={currentValue} name="radio" error={true} />);
        const hasError = wrapper.hasClass('amber-radio-button_error');
        expect(hasError).toBeTruthy();
    });
});
