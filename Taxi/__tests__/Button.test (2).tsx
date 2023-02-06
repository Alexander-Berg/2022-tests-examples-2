import React from 'react';
import {mount, shallow} from 'enzyme';

import TrashIcon from '../../icon/Trash';

import Button from '../Button';

describe('Components/button', () => {
    it('Если есть параметр theme - то применяется соответствующий класс', () => {
        const wrapper = shallow(<Button theme="accent" />);
        expect(wrapper.prop('className')).toContain('amber-button_theme_accent');
    });

    it('Если есть параметр size - то применяется соответствующий класс', () => {
        const wrapper = shallow(<Button size="l" />);
        expect(wrapper.prop('className')).toContain('amber-button_size_l');
    });

    it('Если есть параметр htmlType - тип кнопки соответствующий', () => {
        const type = 'submit';
        const wrapper = shallow(<Button type={type} />);
        expect(wrapper.prop('type')).toEqual(type);
    });

    it('Обработка клика на кнопку', () => {
        const onButtonClick = jest.fn();
        const wrapper = shallow(<Button onClick={onButtonClick} />);
        wrapper.simulate('click');
        expect(onButtonClick.mock.calls.length).toBe(1);
    });

    it('Работает disabled', () => {
        const onButtonClick = jest.fn();
        const wrapper = mount(<Button disabled onClick={onButtonClick} />);
        wrapper.simulate('click');
        expect(onButtonClick.mock.calls.length).toBe(0);
        expect(wrapper.find('button').prop('disabled')).toBeTruthy();
    });

    it('Должны прокидываться иконки', () => {
        const wrapper = shallow(<Button icon={<TrashIcon />} />);
        const wrapper2 = shallow(<Button iconStart={<TrashIcon />}>text</Button>);
        const wrapper3 = shallow(<Button iconEnd={<TrashIcon />}>text</Button>);
        const wrapper4 = shallow(
            <Button iconStart={<TrashIcon />} iconEnd={<TrashIcon />}>
                text
            </Button>
        );
        expect(wrapper.find(TrashIcon)).toHaveLength(1);
        expect(wrapper2.find(TrashIcon)).toHaveLength(1);
        expect(wrapper3.find(TrashIcon)).toHaveLength(1);
        expect(wrapper4.find(TrashIcon)).toHaveLength(2);
    });
});
