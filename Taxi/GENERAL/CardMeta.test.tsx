import React from 'react';
import { shallow } from 'enzyme';

import CardMeta from './CardMeta';

describe('<CardMeta />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<CardMeta />);
    expect(wrapper.exists()).toBe(true);
  });
});
