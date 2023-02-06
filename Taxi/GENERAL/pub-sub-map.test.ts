import {PubSubMap} from './pub-sub-map'

describe('PubSubMap', () => {
  test('clear works and emits update', () => {
    const map = new PubSubMap([[1, 2]])
    const update = jest.fn()

    map.subscribe(update)
    map.clear()

    expect(map.size).toBe(0)
    expect(update).toBeCalledTimes(1)
  })

  test('clear empty map do not emit update', () => {
    const map = new PubSubMap()
    const update = jest.fn()

    map.subscribe(update)
    map.clear()

    expect(update).not.toBeCalled()
  })

  test('clear silent do not emit update', () => {
    const map = new PubSubMap([[1, 2]])
    const update = jest.fn()

    map.subscribe(update)
    map.clear({silent: true})

    expect(map.size).toBe(0)
    expect(update).not.toBeCalled()
  })

  test('delete works and emits update', () => {
    const map = new PubSubMap([[1, 2]])
    const update = jest.fn()

    map.subscribe(update)

    expect(map.delete(1)).toBe(true)
    expect(map.size).toBe(0)
    expect(update).toBeCalledTimes(1)
  })

  test('delete unexisted item do not emit update', () => {
    const map = new PubSubMap([[1, 2]])
    const update = jest.fn()

    map.subscribe(update)

    expect(map.delete(999)).toBe(false)
    expect(map.size).toBe(1)
    expect(update).not.toBeCalled()
  })

  test('delete silent do not emit update', () => {
    const map = new PubSubMap([[1, 2]])
    const update = jest.fn()

    map.subscribe(update)

    expect(map.delete(1, {silent: true})).toBe(true)
    expect(map.size).toBe(0)
    expect(update).not.toBeCalled()
  })

  test('set works and emits update', () => {
    const map = new PubSubMap()
    const update = jest.fn()

    map.subscribe(update)

    expect(map.set(1, 2)).toBe(map)
    expect(map.size).toBe(1)
    expect(map.get(1)).toBe(2)
    expect(update).toBeCalledTimes(1)
  })

  test('set existing key with same value do not emit update', () => {
    const map = new PubSubMap([[1, 2]])
    const update = jest.fn()

    map.subscribe(update)

    expect(map.set(1, 2)).toBe(map)
    expect(map.size).toBe(1)
    expect(map.get(1)).toBe(2)
    expect(update).not.toBeCalled()
  })

  test('set silent do not emit update', () => {
    const map = new PubSubMap()
    const update = jest.fn()

    map.subscribe(update)
    map.set(1, 2, {silent: true})

    expect(update).not.toBeCalled()
  })

  test('submit always emits update', () => {
    const map = new PubSubMap()
    const update = jest.fn()

    map.subscribe(update)
    map.submit()
    map.submit()

    expect(update).toBeCalledTimes(2)
  })
})
