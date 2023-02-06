import React from 'react';
import { shallow } from 'enzyme';

import Logo from './Logo';

describe('<Logo />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(
      <Logo />
    );
    expect(wrapper.exists()).toBe(true);
  });

  it('contains image', () => {
    const wrapper = shallow(<Logo />);
    expect(wrapper.exists('img'));
  });
});
