import { renderHook } from '../testing';
import { useQueryFeatureFlags } from './useQueryFeatureFlags';

describe('useQueryFeatureFlags', () => {
  const { location } = window;

  beforeAll(() => {
    Object.defineProperty(window, 'location', {
      value: {
        search: '?feature=suggest=1&feature=sidebar=1',
      },
      writable: true,
    });
  });

  afterAll(() => {
    Object.defineProperty(window, 'location', {
      value: location,
      writable: true,
    });
  });

  test('should return boolean if feature flag is enabled', () => {
    const { result } = renderHook(() => useQueryFeatureFlags());

    expect(result.current.isEnabled('suggest')).toBeTruthy();
    expect(result.current.isEnabled('sidebar')).toBeTruthy();
    expect(result.current.isEnabled('custom-content')).toBeFalsy();
  });
});
