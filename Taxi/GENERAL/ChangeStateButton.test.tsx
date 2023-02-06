import React from 'react';
import { shallow } from 'enzyme';

import { OfferState } from 'sections/offers/types';

import ChangeStateButton from './ChangeStateButton';

describe('<ChangeStateButton />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(
      <ChangeStateButton
        offerId={42}
        newOfferState={OfferState.Active}
        onClick={jest.fn}
      />
    );
    expect(wrapper.exists()).toBe(true);
  });
});
