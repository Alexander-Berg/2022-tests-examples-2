import {BaseMetrikaProvider} from '../../src/lib/base-metrika-provider'
import {setProvider} from '../../src/lib/metrika'
import {IMetrikaEvents, IMetrikaHitOptions, IMetrikaLogHandler} from '../../src/types'

export function createTestAppMetrika() {
  const mockReachGoal = jest.fn()
  const mockHit = jest.fn()

  /**
   * Реализация для тестов
   */
  class TestAppMetrika extends BaseMetrikaProvider {
    reachGoal<T extends keyof IMetrikaEvents>(
      event: T,
      logHandler: IMetrikaLogHandler<T> | IMetrikaEvents[T],
      clearData = true,
    ) {
      if (typeof logHandler === 'function') {
        mockReachGoal(event, logHandler(this.getEventData(event)))
      } else {
        mockReachGoal(event, logHandler)
      }

      if (clearData) {
        this.clearEventData(event)
      }
    }

    hit(url: string, options?: IMetrikaHitOptions) {
      mockHit(url, options)
    }
  }

  const metrika = new TestAppMetrika()

  setProvider(metrika)

  return {
    metrika,
    mockReachGoal,
    mockHit,
  }
}
