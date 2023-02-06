import React from 'react';
import { shallow } from 'enzyme';

import Result from './Result';

describe('<Result />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(
      <Result
        title='foo'
        subTitle='bar'
        status='info'
      />
    );
    expect(wrapper.exists()).toBe(true);
  });
});
