import {createTestAppMetrika} from '../../../../tests/lib/create-test-app-metrika'
import {addressSearchAnalytics} from '../address-search-analytics'

describe('addressSearchAnalytics', () => {
  it('addressSearchAnalytics.opened', () => {
    const TEST_EVENT = 'lavka.address_search.opened'
    const TEST_DATA = {
      userCoords: {
        lat: 0,
        lon: 0,
      },
      userAddress: '',
      source: 'address_select_modal' as const,
    }

    const {mockReachGoal} = createTestAppMetrika()

    addressSearchAnalytics.opened(TEST_DATA)

    expect(mockReachGoal).toBeCalledTimes(1)
    expect(mockReachGoal).toBeCalledWith(TEST_EVENT, {
      user_address: TEST_DATA.userAddress,
      user_coords: [TEST_DATA.userCoords.lat, TEST_DATA.userCoords.lon],
      source: TEST_DATA.source,
    })
  })
})
