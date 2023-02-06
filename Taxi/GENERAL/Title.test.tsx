import React from 'react';
import { shallow } from 'enzyme';

import Title from './Title';

describe('<Headline />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<Title />);
    expect(wrapper.exists()).toBe(true);
  });
});
