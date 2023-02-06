import React from 'react';
import { shallow } from 'enzyme';

import Popover from './Popover';

describe('<Popover />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<Popover />);
    expect(wrapper.exists()).toBe(true);
  });
});
