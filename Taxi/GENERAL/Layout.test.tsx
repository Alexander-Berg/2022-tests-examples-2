import React from 'react';
import { shallow } from 'enzyme';

import Layout from 'modules/core/components/App/Layout/Layout';

describe('<Layout />', () => {
  it('renders without crashing', () => {
    shallow(<Layout />);
  });

  it('renders its children', () => {
    const wrapper = shallow(
      <Layout>
        <div className='foo'>bar</div>
      </Layout>
    );

    expect(wrapper.contains(<div className='foo'>bar</div>)).toBe(true);
  });
});
