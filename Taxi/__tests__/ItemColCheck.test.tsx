import React from 'react';
import {shallow} from 'enzyme';

import {ITEM_CLASS_NAME} from '../Item';
import ItemColCheck from '../ItemColCheck';
import Check from '../../icon/Check';

test('должен показывать иконку если передали пропс checked', function () {
    const component = shallow(<ItemColCheck checked/>);

    expect(component.find(Check)).toHaveLength(1);
});

test('должен прятать иконку если не передали пропс checked', function () {
    const component = shallow(<ItemColCheck/>);
    const icon = component.find(Check);

    expect(icon).toHaveLength(1);
    expect(icon.hasClass(`${ITEM_CLASS_NAME}__hidden`)).toEqual(true);
});
