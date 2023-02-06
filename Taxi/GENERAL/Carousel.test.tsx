import React from 'react';
import { shallow } from 'enzyme';

import Carousel from './Carousel';

describe('<Carousel />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<Carousel />);
    expect(wrapper.exists()).toBe(true);
  });
});
