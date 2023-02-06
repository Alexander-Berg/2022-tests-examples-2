import React from 'react';
import { shallow } from 'enzyme';

import Spin from './Spin';

describe('<Spin />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<Spin />);
    expect(wrapper.exists()).toBe(true);
  });
});
