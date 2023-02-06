import React from 'react';
import {shallow} from 'enzyme';

import List from '../List';
import Item from '../Item';
import ItemContent from '../ItemContent';

test('должен рендерить заголовок', function () {
    const component = shallow(<List title="title"/>);
    const item = component.find(Item);
    const content = component.find(ItemContent);

    expect(item).toHaveLength(1);
    expect(item.prop('header')).toEqual(true);
    expect(content).toHaveLength(1);
    expect(content.prop('title')).toEqual('title');
    expect(content.dive().text()).toEqual('title');
});
