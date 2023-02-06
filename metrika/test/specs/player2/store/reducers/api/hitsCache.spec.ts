import reducer, { initialState } from '@player2/store/reducers/api/hitsCache'
import { FETCH_HIT, apiSuccess, apiError, fetchHit } from '@player2/store/actions/api'

describe('Timer reducer', () => {
  it('returns correct initial state', () => {
    expect(reducer(
      undefined as any,
      {type: 'init', payload: null as any} as RStore.Action<any>
    )).toEqual(initialState)
  })

  it('handles fetch hit', () => {
    expect(reducer(initialState, fetchHit(0))).toEqual({
      [0]: {
        fetching: true,
      },
    })
  })

  it('handles fetch hit success', () => {
    const state = reducer(
      {
        [0]: {
        fetching: true,
        },
      },
      apiSuccess(FETCH_HIT, 'data', fetchHit(0))
    )
    expect(state).toEqual({
      [0]: {
        fetching: false,
        data: 'data',
      },
    })
  })

  it ('handles fetch hit error', () => {
    const state = reducer(
      {
        [0]: {
          fetching: true,
        },
      },
      apiError(FETCH_HIT, Error('error'), fetchHit(0))
    )
    expect(state).toEqual({
      [0]: {
        fetching: false,
        error: Error('error'),
      },
    })
  })
})
