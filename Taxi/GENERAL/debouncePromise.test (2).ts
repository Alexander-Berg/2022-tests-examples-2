import { noop } from '@lavka/utils'

import { debouncePromise } from './debouncePromise'

jest.useFakeTimers()

describe('debouncePromise', () => {
  beforeEach(() => {
    jest.clearAllTimers()
  })

  it('should call fn after delay', () => {
    const fn = jest.fn(() => Promise.resolve())

    const debounced = debouncePromise(fn, 300)

    debounced().catch(noop)

    expect(fn).not.toBeCalled()

    jest.advanceTimersByTime(300)

    expect(fn).toBeCalled()
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('should call fn one time within given delay', () => {
    const fn = jest.fn(() => Promise.resolve())

    const debounced = debouncePromise(fn, 300)

    debounced().catch(noop)
    debounced().catch(noop)

    jest.advanceTimersByTime(300)

    expect(fn).toBeCalled()
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('should call fn with latest arguments', () => {
    const fn = jest.fn((_arg0: number, _arg1: string) => Promise.resolve())

    const debounced = debouncePromise(fn, 300)

    debounced(1, 'a').catch(noop)
    debounced(2, 'b').catch(noop)

    jest.runAllTimers()

    expect(fn).toBeCalled()
    expect(fn).toHaveBeenCalledWith(2, 'b')
  })

  it('should not call fn after abort', () => {
    const fn = jest.fn(() => Promise.resolve())

    const abortCtrl = new AbortController()
    const debounced = debouncePromise(fn, 300, {
      signal: abortCtrl.signal,
    })

    debounced().catch(noop)

    abortCtrl.abort()

    jest.runAllTimers()

    expect(fn).not.toBeCalled()
  })

  it('should reject previous call with "AbortingError", if abort is called', async () => {
    const fn = jest.fn(() => Promise.resolve())

    const abortCtrl = new AbortController()
    const debounced = debouncePromise(fn, 300, {
      signal: abortCtrl.signal,
    })

    const promise = debounced()

    abortCtrl.abort()

    jest.runAllTimers()

    await expect(promise).rejects.toHaveProperty('name', 'AbortingError')
  })

  it('should reject previous call with "ClearingError", if new one started', async () => {
    const fn = jest.fn((value: number) => Promise.resolve(value))

    const debounced = debouncePromise(fn, 300)

    const promise1 = debounced(1)

    debounced(2).catch(noop)

    jest.runAllTimers()

    await expect(promise1).rejects.toHaveProperty('name', 'ClearingError')
  })

  it('should resolve correct value for the last call', async () => {
    const fn = jest.fn((value: number) => Promise.resolve(value))

    const debounced = debouncePromise(fn, 300)

    debounced(1).catch(noop)

    const promise2 = debounced(2)

    jest.runAllTimers()

    await expect(promise2).resolves.toBe(2)
  })

  it('should call fn with selected arguments', () => {
    const fn = jest.fn((_arg0: number, _arg1: string) => Promise.resolve())

    const debounced = debouncePromise(fn, 300, {
      selectArgs: () => [2, 'overriden'] as [number, string],
    })

    debounced(1, 'original').catch(noop)

    jest.runAllTimers()

    expect(fn).toBeCalledWith(2, 'overriden')
  })

  it('should provide to selectArgs all arguments fn was called with', () => {
    const fn = jest.fn((_arg0: number, _arg1: string) => Promise.resolve())

    const selectArgs = jest.fn().mockReturnValue([])

    const debounced = debouncePromise(fn, 300, {
      selectArgs,
    })

    debounced(1, 'first').catch(noop)
    debounced(2, 'second').catch(noop)

    jest.runAllTimers()

    expect(selectArgs).toBeCalled()
    expect(selectArgs).toHaveBeenCalledTimes(1)
    expect(selectArgs).toHaveBeenCalledWith([
      [1, 'first'],
      [2, 'second'],
    ])
  })
})
