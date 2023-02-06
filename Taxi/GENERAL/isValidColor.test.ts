import {isValidColor} from './isValidColor'

describe('isValidColor', () => {
  test('#fff is valid color', () => {
    expect(isValidColor('#fff')).toBe(true)
  })

  test('#ffff is invalid color', () => {
    expect(isValidColor('#ff')).toBe(false)
  })

  test('#FFF is valid color', () => {
    expect(isValidColor('#FFF')).toBe(true)
  })

  test('white is invalid color', () => {
    expect(isValidColor('white')).toBe(false)
  })

  test('#ffffff is valid color', () => {
    expect(isValidColor('#ffffff')).toBe(true)
  })
})
