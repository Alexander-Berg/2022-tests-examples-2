import createReducer, { initialApiRequestState } from '@player2/utils/apiReducers'
import { SUCCESS_PREFIX, ERROR_PREFIX } from '@player2/store/actions/api'

describe('Api reducer', () => {
  const apiName = 'SOME_API'
  const reducer = createReducer(apiName)

  it('Return correct initial state', () => {
    expect(reducer(undefined as any, {type: 'init', payload: null} as any)).toEqual({fetching: false, data: null})
  })
  let state = initialApiRequestState

  it('Handles fetch', () => {
    state = reducer(state, {type: apiName, payload: null} as any)
    expect(state).toEqual({fetching: true, data: null})
  })

  it('Handles success', () => {
    const data = [1, 2, 3]
    state = reducer(state, {type: SUCCESS_PREFIX + apiName, payload: {data}} as any)
    expect(state).toEqual({fetching: false, data})
  })

  it('Handles error', () => {
    const error = new Error('Something happened')
    state = reducer(state, {type: ERROR_PREFIX + apiName, payload: {error}} as any)
    expect(state).toEqual({fetching: false, error})
  })
})
