import {invariant} from '../invariant'

describe('invariant', () => {
  test('invariant throws', () => {
    expect(() => invariant(undefined)).toThrow()
    expect(() => invariant(null)).toThrow()
    expect(() => invariant(false)).toThrow()
    expect(() => invariant(true)).not.toThrow()
    expect(() => invariant('')).toThrow()
    expect(() => invariant(' ')).not.toThrow()
    expect(() => invariant('test')).not.toThrow()
    expect(() => invariant(0)).toThrow()
    expect(() => invariant(10)).not.toThrow()
    expect(() => invariant(10.1)).not.toThrow()
    expect(() => invariant({})).not.toThrow()
    expect(() => invariant([])).not.toThrow()
  })
})
