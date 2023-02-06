import React from 'react';
import { shallow } from 'enzyme';

import Divider from './Divider';

describe('<Divider />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<Divider />);
    expect(wrapper.exists()).toBe(true);
  });
});
