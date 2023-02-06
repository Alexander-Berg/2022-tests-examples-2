import React from 'react';
import {shallow} from 'enzyme';

import ItemCol, {ITEM_COL_CLASS_NAME} from '../ItemCol';

test(`дожен содержать класс ${ITEM_COL_CLASS_NAME}_grow, если передали пропс grow`, function () {
    const component = shallow(<ItemCol grow/>);

    expect(component.find('div').hasClass(`${ITEM_COL_CLASS_NAME}_grow`)).toEqual(true);
});
