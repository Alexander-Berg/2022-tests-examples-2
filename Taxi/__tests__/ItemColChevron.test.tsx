import React from 'react';
import {shallow} from 'enzyme';

import ItemColChevron from '../ItemColChevron';
import ChevronRight from '../../icon/ChevronRight';

test('должен рендерить иконку стрелочки', function () {
    const component = shallow(<ItemColChevron/>);

    expect(component.find(ChevronRight)).toHaveLength(1);
});
