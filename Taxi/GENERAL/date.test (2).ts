import { getCurrentDateShift } from './date'

const RealDate = Date.now

describe('date utils', () => {
  beforeAll(() => {
    global.Date.now = jest.fn(() => new Date('January 1, 2077 00:00:00').getTime())
  })

  afterAll(() => {
    global.Date.now = RealDate
  })

  test('Should calculate correct date shift from current date', () => {
    const shiftDate = getCurrentDateShift({ years: 1, days: 1, hours: 1, minutes: 1, months: 1, seconds: 1 })

    expect(shiftDate.toISOString()).toEqual('2078-02-02T01:01:01.000Z')
  })
})
