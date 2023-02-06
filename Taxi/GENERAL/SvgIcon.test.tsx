import React from 'react';
import { shallow } from 'enzyme';

import SvgIcon from './SvgIcon';

describe('<SvgIcon />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<SvgIcon icon='star' />);
    expect(wrapper.exists()).toBe(true);
  });
});
