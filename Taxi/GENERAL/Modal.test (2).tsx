import React from 'react';
import { shallow } from 'enzyme';

import Modal from './Modal';

describe('<Modal />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<Modal />);
    expect(wrapper.exists()).toBe(true);
  });
});
