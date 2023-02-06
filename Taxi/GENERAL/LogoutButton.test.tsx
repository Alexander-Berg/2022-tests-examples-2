import React from 'react';
import { shallow } from 'enzyme';

import LogoutButton from './LogoutButton';

describe('<LogoutButton />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<LogoutButton isLoggedIn />);
    expect(wrapper.exists()).toBe(true);
  });
});
