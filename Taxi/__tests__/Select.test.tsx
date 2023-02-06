import React from 'react';
import {shallow} from 'enzyme';
import Select from '../Select';

const OPTIONS = [{value: 'russia', label: 'Россия'}, {value: 'brazil', label: 'Бразилия'}];

describe('Components/select', () => {
    it('Если есть параметр className - то применяется соответствующий класс', () => {
        const customClassName = 'fifa2018';
        const wrapper = shallow(
            <Select
                className={customClassName}
                value="russia"
                options={OPTIONS}
            />
        );
        expect(wrapper.prop('className')).toContain(customClassName);
    });

    // что за фейковый тест,
    it('Если есть параметр multi - то применяется соответствующий класс', () => {
        const multiClassName = 'Select--multi';
        const wrapper = shallow(
            <Select
                className={multiClassName}
                value="russia"
                options={OPTIONS}
            />
        );
        expect(wrapper.prop('className')).toContain(multiClassName);
    });
});
