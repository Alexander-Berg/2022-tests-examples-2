import { formatPhoneNumber } from 'utils/formatPhoneNumber';

describe('formatPhoneNumber', () => {
  it('successfully parses valid input with country code', () => {
    expect(formatPhoneNumber('89991234567')).toBe('+7 999 123 45 67');
  });

  it('successfully parses valid input without country code', () => {
    expect(formatPhoneNumber('8121234567')).toBe('+7 812 123 45 67');
  });

  it('returns input value as string if parsing failed', () => {
    const phoneAsNumber = 42;
    const phoneAsString = '42';
    expect(formatPhoneNumber(phoneAsNumber)).toBe('42');
    expect(formatPhoneNumber(phoneAsString)).toBe('42');
  });
});
