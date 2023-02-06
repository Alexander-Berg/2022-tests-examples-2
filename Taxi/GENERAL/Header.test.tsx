import React from 'react';
import { shallow } from 'enzyme';

import Logo from './Logo';
import Header from './Header';

describe('<Header />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<Header />);
    expect(wrapper.exists()).toBe(true);
  });

  it('has logo inside', () => {
    const wrapper = shallow(<Header />);
    expect(wrapper.find(Logo)).toHaveLength(1);
  });
});
