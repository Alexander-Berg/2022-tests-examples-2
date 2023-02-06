import React from 'react';
import { shallow } from 'enzyme';

import FilterForm from './FilterForm';

describe('<FilterForm />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<FilterForm />);
    expect(wrapper.exists()).toBe(true);
  });
});
