import React from 'react';
import { shallow } from 'enzyme';

import Alert from './Alert';

describe('<Alert />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(
      <Alert message='foo' />
    );
    expect(wrapper.exists()).toBe(true);
  });
});
