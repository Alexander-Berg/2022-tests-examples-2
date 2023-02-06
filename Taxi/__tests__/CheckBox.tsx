import {shallow} from 'enzyme';
import React from 'react';

import CheckBox from '..';

describe('CheckBox', () => {
    it('обычный рендер', () => {
        const checkbox = shallow(<CheckBox label="label"/>);

        expect(checkbox).toMatchSnapshot();
    });

    it('должен вызываться onChange с правильными параметрами', () => {
        const target = {
            name: 'name',
            checked: true,
        };
        const onChange = jest.fn();
        const checkbox = shallow(<CheckBox label="label" onChange={onChange}/>);

        checkbox.find('input').simulate('change', {target});

        expect(onChange).toHaveBeenCalledTimes(1);
        expect(onChange.mock.calls[0][0]).toEqual(target);
    });
});
