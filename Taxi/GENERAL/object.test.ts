/* eslint-disable @typescript-eslint/no-unused-vars */
import {fromEntries, keys, mapEntries, mapKeys, mapValues, values} from './object'

type TestData = {
  foo: string
  bar: number
}

const testData: TestData = {foo: 'foo1', bar: 847}

describe('`keys` and `values` getters', () => {
  it('works like innate methods', () => {
    expect(keys(testData)).toEqual(Object.keys(testData))
    expect(values(testData)).toEqual(Object.values(testData))
  })

  it('returns the correct type', () => {
    const k: (keyof TestData)[] = keys(testData)
    const v: TestData[keyof TestData][] = values(testData)

    // тест проверяет только типы, в рантайме нечего смотреть
    expect(true).toBe(true)
  })
})

describe('`mapKeys` function', () => {
  it('works correctly', () => {
    expect(mapKeys((k, v) => `${k}${v}`, testData)).toEqual({foofoo1: testData.foo, bar847: testData.bar})
    expect(mapKeys(k => `${testData[k]}`, testData)).toEqual({foo1: 'foo1', '847': 847})
  })
})

describe('`mapValues` function', () => {
  it('works correctly', () => {
    expect(mapValues((value, key) => `${key}${value}`, testData)).toEqual({foo: 'foofoo1', bar: 'bar847'})
  })
})

describe('`mapEntries` function', () => {
  it('works correctly', () => {
    expect(mapEntries((key, value) => [value, key], testData)).toEqual({foo1: 'foo', '847': 'bar'})
    expect(mapEntries(key => [testData[key], key], testData)).toEqual({foo1: 'foo', '847': 'bar'})
  })
})

describe('`fromEntries` function', () => {
  it('works correctly', () => {
    expect(fromEntries(Object.entries(testData))).toEqual(testData)
  })
})
