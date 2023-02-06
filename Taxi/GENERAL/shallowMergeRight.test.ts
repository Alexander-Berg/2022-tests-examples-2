import {shallowMergeRight} from './shallowMergeRight'

type TestType = {
  foo: number
  bar: {
    version: number
    data?: number
  }
  baz: number
}

describe('shallowMergeRight', () => {
  it('should not mutate arguments', () => {
    const a = {foo: 0, bar: 0}
    const b = {bar: 1, baz: 1}

    shallowMergeRight(a, b)

    expect(a).toStrictEqual({foo: 0, bar: 0})
    expect(b).toStrictEqual({bar: 1, baz: 1})
  })

  it('should merge shallowly', () => {
    const a: Partial<TestType> = {foo: 0, bar: {version: 0, data: 0}}
    const b: Partial<TestType> = {bar: {version: 1}, baz: 1}

    const actual = shallowMergeRight(a, b)

    expect(actual).toStrictEqual({foo: 0, bar: {version: 1}, baz: 1})
  })
})
