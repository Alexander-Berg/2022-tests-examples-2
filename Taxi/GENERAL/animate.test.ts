import {animate} from '@lavka/ui'

jest.useFakeTimers()

let spyRaf: jest.SpyInstance
let spyCaf: jest.SpyInstance

beforeEach(() => {
  let ds = 0
  spyRaf = jest.spyOn(window, 'requestAnimationFrame').mockImplementation(fn => {
    ds += 100
    // перебивается типом setTimeout из node.js
    return Number(setTimeout(fn, 0, ds))
  })

  spyCaf = jest.spyOn(window, 'cancelAnimationFrame').mockImplementation(timerId => {
    clearTimeout(timerId)
  })
})

afterEach(() => {
  spyRaf.mockRestore()
  spyCaf.mockRestore()
})

describe('animate', () => {
  test('animation callback is called', () => {
    const callback = jest.fn()

    animate(1000, t => t, callback)

    jest.runOnlyPendingTimers()

    expect(callback).toBeCalled()
  })

  test('cancel animation works', () => {
    const callback = jest.fn()

    const cancelAnimation = animate(1000, t => t, callback)

    cancelAnimation()

    jest.runOnlyPendingTimers()

    expect(callback).not.toBeCalled()
  })

  test.skip('animate counts progress', () => {
    const callback = jest.fn()

    animate(1000, t => t, callback)

    jest.runOnlyPendingTimers()

    expect(callback).toBeCalledWith(0, 0)

    jest.runOnlyPendingTimers()

    expect(callback).toBeCalledWith(0.2, 0.2)
  })
})
