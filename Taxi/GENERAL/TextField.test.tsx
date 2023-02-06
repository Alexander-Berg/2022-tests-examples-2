import React from 'react';
import { shallow } from 'enzyme';

import TextField from './TextField';

describe('<TextField />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<TextField />);
    expect(wrapper.exists()).toBe(true);
  });
});
