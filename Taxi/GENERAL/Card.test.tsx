import React from 'react';
import { shallow } from 'enzyme';

import Card from './Card';

describe('<Card />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<Card />);
    expect(wrapper.exists()).toBe(true);
  });
});
