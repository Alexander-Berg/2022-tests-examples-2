import {shallow} from 'enzyme';
import React from 'react';

import CarNumber from '../CarNumber';

describe('CarNumber', () => {
    it('обычный номер', () => {
        const component = shallow(<CarNumber number="я000ьь99"/>);

        expect(component).toMatchSnapshot();
    });

    it('желтый номер', () => {
        const component = shallow(<CarNumber number="яя00099"/>);

        expect(component).toMatchSnapshot();
    });

    it('ни обычный, ни желтый номер', () => {
        const component = shallow(<CarNumber number="not-valid"/>);

        expect(component).toMatchSnapshot();
    });
});
