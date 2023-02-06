import {shallow} from 'enzyme';
import React from 'react';

import Forbidden from './index';

test('Forbidden should render', () => {
    const ForbiddenComponent = shallow(<Forbidden/>);

    expect(ForbiddenComponent).toMatchSnapshot();
});
