import {isNullable, isNumber} from '../validators/primitives'

describe('parsers', () => {
  test('isNullable', () => {
    expect(isNullable(null)).toBe(true)
    expect(isNullable(undefined)).toBe(true)
    expect(isNullable('')).toBe(false)
    expect(isNullable(' ')).toBe(false)
    expect(isNullable('test')).toBe(false)
    expect(isNullable(0)).toBe(false)
    expect(isNullable(10)).toBe(false)
    expect(isNullable(10.1)).toBe(false)
    expect(isNullable(NaN)).toBe(false)
    expect(isNullable(Infinity)).toBe(false)
    expect(isNullable(false)).toBe(false)
    expect(isNullable(true)).toBe(false)
    expect(isNullable({})).toBe(false)
    expect(isNullable([])).toBe(false)
  })

  test('isNumber', () => {
    expect(isNumber(null)).toBe(false)
    expect(isNumber(undefined)).toBe(false)
    expect(isNumber('')).toBe(false)
    expect(isNumber(' ')).toBe(false)
    expect(isNumber('test')).toBe(false)
    expect(isNumber(0)).toBe(true)
    expect(isNumber(10)).toBe(true)
    expect(isNumber(10.1)).toBe(true)
    expect(isNumber(NaN)).toBe(false)
    expect(isNumber(Infinity)).toBe(true)
    expect(isNumber('0')).toBe(true)
    expect(isNumber('10')).toBe(true)
    expect(isNumber('10.1')).toBe(true)
    expect(isNumber('NaN')).toBe(false)
    expect(isNumber('Infinity')).toBe(true)
  })
})
