import { getCookie } from './getCookie';

describe('getCookie', () => {
  Object.defineProperty(window.document, 'cookie', {
    value: 'foo=bar; baz=42'
  });

  it('returns cookie if key is found', () => {
    expect(getCookie('foo')).toBe('bar');
    expect(getCookie('baz')).toBe('42');
  });

  it('returns undefined if key not found', () => {
    expect(getCookie('bar')).toBe(undefined);
  });
});
