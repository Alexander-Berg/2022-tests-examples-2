import { Offer } from 'sections/offers/types';

import { getLogEntries } from './getLogEntries';

// TODO: add more test cases
describe('getLogEntries', () => {
  it('returns single `create` entry when no other actions present', () => {
    const offer = {
      createdDate: '01.01.1970'
    } as Offer;

    expect(getLogEntries(offer)).toStrictEqual([
      {
        timestamp: '01.01.1970',
        action: { _tag: 'create' }
      }
    ]);
  });

  it('returns `edit` and `changeState` actions when available', () => {
    const offer = {
      createdDate: '01.01.1970',
      state: 'active',
      statesLog: {
        changeDate: '02.01.1970',
        actionDate: '03.01.1970',
        moderatorLogin: 'foo',
        companyUserLogin: 'bar'
      }
    } as Offer;

    expect(getLogEntries(offer)).toStrictEqual([
      {
        timestamp: '01.01.1970',
        action: { _tag: 'create' }
      },
      {
        timestamp: '02.01.1970',
        action: { _tag: 'edit' },
        account: { username: 'bar', fromTaxiPark: true }
      },
      {
        timestamp: '03.01.1970',
        action: { _tag: 'changeState', newState: 'active' },
        account: { username: 'foo', fromTaxiPark: false }
      }
    ]);
  });
});
