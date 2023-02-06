import React from 'react';
import { shallow } from 'enzyme';

import DatePicker from './DatePicker';

describe('<DatePicker />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<DatePicker />);
    expect(wrapper.exists()).toBe(true);
  });
});
