import {getColorLightness} from './colors'

describe('getColorLightness', () => {
  test('lightness of #fff is 1', () => {
    expect(getColorLightness('#fff')).toBe(1)
  })

  test('lightness of #ffffff is 1', () => {
    expect(getColorLightness('#ffffff')).toBe(1)
  })

  test('lightness of #000 is 0', () => {
    expect(getColorLightness('#000')).toBe(0)
  })

  test('lightness of #000000 is 0', () => {
    expect(getColorLightness('#000000')).toBe(0)
  })

  test('lightness of #00ff00 is 0.5', () => {
    expect(getColorLightness('#00ff00')).toBe(0.5)
  })

  test('lightness of #f0f is 1', () => {
    expect(getColorLightness('#f0f')).toBe(0.5)
  })

  test('lightness of #ccc is 0.8', () => {
    expect(getColorLightness('#ccc')).toBe(0.8)
  })
})
