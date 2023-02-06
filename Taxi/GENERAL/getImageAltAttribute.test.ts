import { getImageAltAttribute } from './getImageAltAttribute';

describe('getImageAltAttribute', () => {
  it('works as expected', () => {
    expect(getImageAltAttribute(
      'Cadillac',
      'Escalade',
      2018
    )).toBe('Cadillac Escalade 2018');
  });

  it('does not add year if null', () => {
    expect(getImageAltAttribute(
      'Cadillac',
      'Escalade',
      null
    )).toBe('Cadillac Escalade');
  });
});
