import type { OnscreenTimer } from './OnscreenCounter'
import { OnscreenCounter } from './OnscreenCounter'

class MockTimer implements OnscreenTimer {
  private time = 12345

  getTime() {
    return this.time
  }

  addTime(time: number) {
    this.time += time
  }
}

describe('OnscreenCounter', () => {
  test('One in-out', () => {
    const timer = new MockTimer()
    const counter = new OnscreenCounter(timer)

    counter.setInView('foo')
    timer.addTime(1000)
    counter.setOutOfView('foo')

    expect(counter.getTotalScreenTime('foo')).toBe(1000)
  })

  test('One in', () => {
    const timer = new MockTimer()
    const counter = new OnscreenCounter(timer)

    counter.setInView('foo')
    timer.addTime(1000)

    expect(counter.getTotalScreenTime('foo')).toBe(1000)
  })

  test('One out', () => {
    const timer = new MockTimer()
    const counter = new OnscreenCounter(timer)

    timer.addTime(1000)
    counter.setOutOfView('foo')

    expect(counter.getTotalScreenTime('foo')).toBe(0)
  })

  test('Unknown', () => {
    const counter = new OnscreenCounter()
    expect(counter.getTotalScreenTime('unknown')).toBe(0)
  })

  test('Many', () => {
    const timer = new MockTimer()
    const counter = new OnscreenCounter(timer)

    counter.setInView('foo')
    timer.addTime(1000)

    counter.setInView('bar')
    timer.addTime(1000)

    counter.setOutOfView('foo')
    timer.addTime(500)

    expect(counter.getTotalScreenTime('foo')).toBe(2000)
    expect(counter.getTotalScreenTime('bar')).toBe(1500)
  })
})
