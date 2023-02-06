/* eslint-disable no-extend-native */
import {flatMap} from './flatMap'

const testArr = ['1', '2', '3', '4', '5']

const buffer = Array.prototype.flatMap
// @ts-expect-error
Array.prototype.flatMap = undefined

describe('`flatMap` function', () => {
  it('works on empty errays', () => {
    const f = (n: string) => parseInt(n)
    expect(flatMap(f, [])).toEqual([])
    expect(flatMap(f)([])).toEqual([])
  })

  it('works like regular map', () => {
    const f = (n: string) => parseInt(n)
    expect(flatMap(f, testArr)).toEqual(testArr.map(f))
    expect(flatMap(f)(testArr)).toEqual(testArr.map(f))
  })

  it('works like regular map with [] wrapper', () => {
    const flatCallback = (n: string) => [parseInt(n)]
    const callback = (n: string) => parseInt(n)
    expect(flatMap(flatCallback, testArr)).toEqual(testArr.map(callback))
    expect(flatMap(flatCallback)(testArr)).toEqual(testArr.map(callback))
  })

  it('works with adding elements', () => {
    const f = (n: string) => [n, n]
    expect(flatMap(f, testArr)).toEqual(testArr.reduce<string[]>((acc, el) => [...acc, el, el], []))
    expect(flatMap(f)(testArr)).toEqual(testArr.reduce<string[]>((acc, el) => [...acc, el, el], []))
  })

  it('works with deleting elements', () => {
    const f = () => []
    expect(flatMap(f, testArr)).toEqual([])
    expect(flatMap(f)(testArr)).toEqual([])
  })

  it('only flattens once', () => {
    const f = (n: string) => [[n]]
    expect(flatMap(f, testArr)).toEqual(testArr.map(n => [n]))
    expect(flatMap(f)(testArr)).toEqual(testArr.map(n => [n]))
  })
})

Array.prototype.flatMap = buffer
