import React from 'react';
import { shallow } from 'enzyme';

import Tag from './Tag';

describe('<Tag />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<Tag />);
    expect(wrapper.exists()).toBe(true);
  });
});
