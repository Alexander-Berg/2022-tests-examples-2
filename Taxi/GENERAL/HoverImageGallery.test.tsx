import React from 'react';
import { shallow } from 'enzyme';

import HoverImageGallery from './HoverImageGallery';

describe('<HoverImageGallery />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<HoverImageGallery />);
    expect(wrapper.exists()).toBe(true);
  });
});
