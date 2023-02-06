import {createTestAppMetrika} from '../../../tests/lib/create-test-app-metrika'
import {IMetrikaEvents} from '../../types'

describe('metrika', () => {
  const TEST_EVENT = 'lavka.address_search.opened'
  const TEST_DATA: IMetrikaEvents['lavka.address_search.opened'] = {
    user_coords: [],
    user_address: '',
    source: 'address_select_modal',
  }

  it('reachGoal', () => {
    const {metrika, mockReachGoal} = createTestAppMetrika()

    metrika.reachGoal(TEST_EVENT, TEST_DATA)

    expect(mockReachGoal).toBeCalledTimes(1)
    expect(mockReachGoal).toBeCalledWith(TEST_EVENT, TEST_DATA)
  })

  it('reachGoal + logHandler', () => {
    const {metrika, mockReachGoal} = createTestAppMetrika()

    metrika.pushEventData(TEST_EVENT, {
      user_address: 'test address',
    })
    metrika.reachGoal(TEST_EVENT, data => {
      return {...TEST_DATA, ...data}
    })

    expect(mockReachGoal).toBeCalledTimes(1)
    expect(mockReachGoal).toBeCalledWith(TEST_EVENT, {
      ...TEST_DATA,
      user_address: 'test address',
    })
  })

  it('hit', () => {
    const {metrika, mockHit} = createTestAppMetrika()

    metrika.hit('/', {title: 'lavka'})

    expect(mockHit).toBeCalledTimes(1)
    expect(mockHit).toBeCalledWith('/', {title: 'lavka'})
  })
})
