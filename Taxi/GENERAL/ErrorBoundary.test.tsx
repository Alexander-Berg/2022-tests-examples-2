import React from 'react';
import { shallow } from 'enzyme';

import ErrorBoundary from './ErrorBoundary';

describe('<ErrorBoundary />', () => {
  const Fallback = () => (
    <span className='foo'>fallback</span>
  );

  const Dummy = () => (
    <div className='foo'>bar</div>
  );

  it('renders without crashing', () => {
    const wrapper = shallow(<ErrorBoundary />);
    expect(wrapper.exists()).toBe(true);
  });

  it('renders its children when there are no runtime errors', () => {
    const wrapper = shallow(
      <ErrorBoundary fallback={<Fallback />}>
        <Dummy />
      </ErrorBoundary>
    );

    expect(wrapper.contains(<Dummy />)).toBe(true);
    expect(wrapper.contains(<Fallback />)).toBe(false);
  });

  it('renders fallback when a runtime error is caught', () => {
    const wrapper = shallow(
      <ErrorBoundary fallback={<Fallback />}>
        <Dummy />
      </ErrorBoundary>
    );

    const error = new Error('Crashed!');
    wrapper.find(Dummy).simulateError(error);

    expect(wrapper.state()).toHaveProperty('error', error);
    expect(wrapper.contains(<Dummy />)).toBe(false);
    expect(wrapper.contains(<Fallback />)).toBe(true);
  });
});
