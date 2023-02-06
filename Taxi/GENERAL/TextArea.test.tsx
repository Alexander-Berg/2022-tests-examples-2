import React from 'react';
import { shallow } from 'enzyme';

import TextArea from './TextArea';

describe('<TextArea />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<TextArea />);
    expect(wrapper.exists()).toBe(true);
  });
});
