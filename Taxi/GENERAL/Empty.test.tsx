import React from 'react';
import { shallow } from 'enzyme';

import Empty from './Empty';

describe('<Empty />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<Empty />);
    expect(wrapper.exists()).toBe(true);
  });
});
