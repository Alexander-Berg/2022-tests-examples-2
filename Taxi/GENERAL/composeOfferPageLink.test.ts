import { composeOfferPageLink } from './composeOfferPageLink';

describe('composeOfferPageLink', () => {
  it('works as expected without origin provided', () => {
    expect(composeOfferPageLink('foo', 42)).toBe('/foo/arenda_auto_42');
  });

  it('works as expected with origin provided', () => {
    const origin = 'https://yandex.ru';
    const expected = `${origin}/foo/arenda_auto_42`;
    expect(composeOfferPageLink('foo', 42, origin)).toBe(expected);
  });
});
