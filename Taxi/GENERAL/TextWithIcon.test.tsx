import React from 'react';
import { shallow } from 'enzyme';

import TextWithIcon from './TextWithIcon';

describe('<TextWithIcon />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<TextWithIcon label='label' />);
    expect(wrapper.exists()).toBe(true);
  });
});
