import { formatDateString } from './formatDateString';

describe('formatDateString', () => {
  it('parses correct date', () => {
    const dateString = '2019-06-14T07:01:01.49931';
    expect(formatDateString(dateString)).toBe('14.06.2019, 07:01:01');
  });

  it('if argument string has an invalid format, return as is', () => {
    expect(formatDateString('foobar')).toBe('foobar');
  });
});
