import reducer from '@player2/store/reducers/currentHit'
import { setCurrentHit } from '@player2/store/actions/currentHit'

describe('current hit reducer', () => {
  it('Sets current hit and calculates additional scroll events', () => {
    const currentHit = {
        events: [
          {
            type: 'page',
            stamp: 0,
          },
          {
            type: 'scroll',
            meta: {x: 10, y: 0},
            stamp: 0,
            target: 1,
          },
          {
            type: 'scroll',
            meta: {x: 30, y: 0},
            stamp: 80,
            target: 1,
          },
          {
            type: 'scroll',
            meta: {x: 25, y: 0},
            stamp: 160,
            target: 1,
          },
          {
            type: 'scroll',
            meta: {y: 0, x: 0},
            stamp: 2000,
            target: 1,
          },
          {
            type: 'someEvent',
            meta: {y: 20, x: 0},
            stamp: 2040,
            target: 1,
          },
          {
            type: 'scroll',
            meta: {y: 20, x: 0},
            stamp: 2040,
            target: 1,
          },
          {
            type: 'someEvent',
            stamp: 3000,
          },
        ],
      }

      const processedHit = {
        events: [
          {
            type: 'page',
            stamp: 0,
          },
          {
            type: 'scroll',
            meta: {x: 10, y: 0},
            stamp: 0,
            target: 1,
          },
          {
            type: 'scroll',
            meta: {x: 15, y: 0},
            stamp: 20,
            target: 1,
          },
          {
            type: 'scroll',
            meta: {x: 20, y: 0},
            stamp: 40,
            target: 1,
          },
          {
            type: 'scroll',
            meta: {x: 25, y: 0},
            stamp: 60,
            target: 1,
          },
          {
            type: 'scroll',
            meta: {x: 30, y: 0},
            stamp: 80,
            target: 1,
          },
          {
            type: 'scroll',
            meta: {x: 25, y: 0},
            stamp: 160,
            target: 1,
          },
          {
            type: 'scroll',
            meta: {y: 0, x: 0},
            stamp: 2000,
            target: 1,
          },
          {
            type: 'scroll',
            meta: {y: 10, x: 0},
            stamp: 2020,
            target: 1,
          },
          {
            type: 'someEvent',
            meta: {y: 20, x: 0},
            stamp: 2040,
            target: 1,
          },
          {
            type: 'scroll',
            meta: {y: 20, x: 0},
            stamp: 2040,
            target: 1,
          },
          {
            type: 'someEvent',
            stamp: 3000,
          },
        ],
      }

      const state = reducer(undefined, setCurrentHit(currentHit))
      expect(state).toEqual(processedHit)
  })
})
