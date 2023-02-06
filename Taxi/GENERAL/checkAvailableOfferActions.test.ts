import { OfferState } from 'sections/offers/types';

import {
  canBeActivated,
  canBeModerated,
  canBeRaised,
  canBeRejected
} from './checkAvailableOfferActions';

describe('checkAvailableOfferActions', () => {
  const states = [
    OfferState.Active,
    OfferState.Moderate,
    OfferState.Rejected,
    OfferState.Draft,
    OfferState.Completed
  ];

  describe('canBeActivated', () => {
    it('returns `true` if state is neither `Active` nor `Draft`', () => {
      expect(states.filter(canBeActivated)).toStrictEqual([
        OfferState.Moderate,
        OfferState.Rejected,
        OfferState.Completed
      ]);
    });
  });

  describe('canBeModerated', () => {
    it('returns `true` if state is `Rejected`', () => {
      expect(states.filter(canBeModerated)).toStrictEqual([
        OfferState.Rejected
      ]);
    });
  });

  describe('canBeRaised', () => {
    it('returns `true` if state is `Active`', () => {
      expect(states.filter(canBeRaised)).toStrictEqual([
        OfferState.Active
      ]);
    });
  });

  describe('canBeRejected', () => {
    it('returns `true` if state is neither `Draft` nor `Rejected`', () => {
      expect(states.filter(canBeRejected)).toStrictEqual([
        OfferState.Active,
        OfferState.Moderate,
        OfferState.Completed
      ]);
    });
  });
});
