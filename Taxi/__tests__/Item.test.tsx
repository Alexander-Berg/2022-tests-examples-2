import React from 'react';
import {shallow} from 'enzyme';

import Item, {ITEM_CLASS_NAME} from '../Item';

test(`должен иметь класс ${ITEM_CLASS_NAME}_header, если передали пропс header`, function () {
    const component = shallow(<Item header/>);

    expect(component.find('li').hasClass(`${ITEM_CLASS_NAME}_header`)).toEqual(true);
});

test(`должен иметь класс ${ITEM_CLASS_NAME}_interactive, если передали пропс onClick или onKeyDown`, function () {
    const component = shallow(<Item onClick={() => null}/>);

    expect(component.find('li').hasClass(`${ITEM_CLASS_NAME}_interactive`)).toEqual(true);
});
