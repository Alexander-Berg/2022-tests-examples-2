import React from 'react';
import { shallow } from 'enzyme';

import PhoneNumber from './PhoneNumber';

describe('<PhoneNumber />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<PhoneNumber phone='79117774242' />);
    expect(wrapper.exists()).toBe(true);
  });
});
