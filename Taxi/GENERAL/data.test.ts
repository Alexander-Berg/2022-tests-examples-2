import {parseISODate} from './date'

describe('lib', () => {
  describe('date', () => {
    describe('date', () => {
      describe('parseISODate', () => {
        it('should work', () => {
          parseISODate('2018-12-17T10:31:20+03:00')
        })

        it('should return a parsed object', () => {
          const res = parseISODate('2018-12-17T10:31:20+03:00')

          expect(res).toHaveProperty('year')
          expect(res).toHaveProperty('month')
          expect(res).toHaveProperty('day')
          expect(res).toHaveProperty('hours')
          expect(res).toHaveProperty('minutes')
          expect(res).toHaveProperty('seconds')
          expect(res).toHaveProperty('hoursOffset')
        })

        it('should return a valid object', () => {
          const res = parseISODate('2018-12-17T10:31:20+03:00')

          expect(res).toEqual({
            year: 2018,
            month: 12,
            day: 17,
            hours: 10,
            minutes: 31,
            seconds: 20,
            hoursOffset: 3,
          })
        })

        it('should support a negative time offset', () => {
          const res = parseISODate('2018-12-17T10:31:20-05:00')

          expect(res.hoursOffset).toEqual(-5)
        })

        it('should support the Z time offset', () => {
          const res = parseISODate('2018-12-17T10:31:20Z')

          expect(res.hoursOffset).toEqual(0)
        })
      })
    })
  })
})
