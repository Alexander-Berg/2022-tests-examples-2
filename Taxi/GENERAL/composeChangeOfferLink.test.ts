import { composeChangeOfferLink } from './composeChangeOfferLink';

describe('composeChangeOfferLink', () => {
  it('works as expected without origin provided', () => {
    expect(composeChangeOfferLink(42)).toBe('/admin/offers/change/42');
  });

  it('works as expected with origin provided', () => {
    const origin = 'https://yandex.ru';
    const expected = `${origin}/admin/offers/change/42`;
    expect(composeChangeOfferLink(42, origin)).toBe(expected);
  });
});
