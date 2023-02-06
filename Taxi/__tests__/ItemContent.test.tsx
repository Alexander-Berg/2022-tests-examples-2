import React from 'react';
import {shallow} from 'enzyme';

import ItemContent from '../ItemContent';

test('должен рендерить title', function () {
    const component = shallow(<ItemContent title="title"/>);

    expect(component.text()).toEqual('title');
});

test('должен рендерить вместо title компонент', function () {
    const Custom = () => <div/>;
    const component = shallow(<ItemContent title={<Custom/>}/>);

    expect(component.find(Custom)).toHaveLength(1);
});

test('должен рендерить description', function () {
    const component = shallow(<ItemContent title="" description="description"/>);

    expect(component.text()).toEqual('description');
});

test('должен рендерить вместо description компонент', function () {
    const Custom = () => <div/>;
    const component = shallow(<ItemContent title="" description={<Custom/>}/>);

    expect(component.find(Custom)).toHaveLength(1);
});
