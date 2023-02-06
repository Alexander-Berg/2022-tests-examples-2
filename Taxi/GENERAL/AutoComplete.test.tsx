import React from 'react';
import { shallow } from 'enzyme';

import AutoComplete from './AutoComplete';

describe('<AutoComplete />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<AutoComplete />);
    expect(wrapper.exists()).toBe(true);
  });
});
