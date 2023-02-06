import React from 'react';
import { shallow } from 'enzyme';

import PageContent from './PageContent';

describe('<PageContent />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(<PageContent />);
    expect(wrapper.exists()).toBe(true);
  });

  it('renders its children', () => {
    const wrapper = shallow(
      <PageContent>
        <div className='foo'>bar</div>
      </PageContent>
    );

    expect(wrapper.contains(<div className='foo'>bar</div>)).toBe(true);
  });
});
