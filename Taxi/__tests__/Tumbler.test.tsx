import {shallow} from 'enzyme';
import React from 'react';
import Tumbler from '../Tumbler';

describe('Components/tumbler', () => {
    it('Передача атрибута disabled', () => {
        const wrapper = shallow(<Tumbler disabled label="Жми меня" />);
        expect(
            wrapper
                .dive()
                .find('input')
                .prop('disabled')
        ).toBeTruthy();
    });

    it('Передача атрибута checked', () => {
        const wrapper = shallow(<Tumbler checked label="Жми меня" />);
        expect(
            wrapper
                .dive()
                .find('input')
                .prop('checked')
        ).toBeTruthy();
    });

    it('Передача label', () => {
        const labelText = 'Жми меня';
        const wrapper = shallow(<Tumbler checked label={labelText} />);
        expect(
            wrapper
                .dive()
                .find('label')
                .text()
        ).toEqual(labelText);
    });
});
