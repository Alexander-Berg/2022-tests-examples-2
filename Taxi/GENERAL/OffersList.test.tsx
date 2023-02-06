import React from 'react';
import { shallow } from 'enzyme';

import { OfferState } from 'sections/offers/types';
import OffersList from './OffersList';

describe('<OffersList />', () => {
  it('renders without crashing', () => {
    const wrapper = shallow(
      <OffersList
        state={OfferState.Active}
        items={[]}
        loading={false}
        currentPage={0}
        totalOffers={0}
        defaultPageSize={10}
        onPageChange={(page, pageSize) => {
        }}
      />
    );
    expect(wrapper.exists()).toBe(true);
  });
});
