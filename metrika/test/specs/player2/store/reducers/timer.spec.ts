import { play, tick, pause, setReady, setFinished, rewind } from '@player2/store/actions/timer'
import reducer, { initialState, DEFAULT_PLAY_SPEED } from '@player2/store/reducers/timer'

describe('Timer reducer', () => {
  it('returns correct initial state', () => {
    const state = reducer(undefined as any, {type: 'init', payload: null} as any)
    expect(state).toEqual({
      time: 0,
      speed: DEFAULT_PLAY_SPEED,
      playing: false,
      ready: false,
      finished: false,
      rewinding: false,
    })
  })

  it('handles rewind', () => {
    const state = reducer(initialState, rewind(10))
    expect(state).toEqual({
      time: 10,
      speed: DEFAULT_PLAY_SPEED,
      playing: false,
      ready: false,
      finished: false,
      rewinding: true,
    })
  })

  it('handles play', () => {
    const state = reducer(initialState, play())
    expect(state).toEqual({
      time: 0,
      speed: DEFAULT_PLAY_SPEED,
      playing: true,
      ready: false,
      finished: false,
      rewinding: false,
    })
  })

  it('handles tick', () => {
    const state = reducer(initialState, tick(100))
    expect(state).toEqual({
      time: 100,
      speed: DEFAULT_PLAY_SPEED,
      playing: false,
      ready: false,
      finished: false,
      rewinding: false,
    })
  })

  it('handles pause', () => {
    const state = reducer(initialState, pause())
    expect(state).toEqual({
      time: 0,
      speed: DEFAULT_PLAY_SPEED,
      playing: false,
      ready: false,
      finished: false,
      rewinding: false,
    })
  })

  it('handles setReady', () => {
    const state = reducer({...initialState, rewinding: true}, setReady(true))
    expect(state).toEqual({
      time: 0,
      speed: DEFAULT_PLAY_SPEED,
      playing: false,
      ready: true,
      finished: false,
      rewinding: false,
    })
  })

  it('handles setFinished', () => {
    const state = reducer(initialState, setFinished(true))
    expect(state).toEqual({
      time: 0,
      speed: DEFAULT_PLAY_SPEED,
      playing: false,
      ready: false,
      finished: true,
      rewinding: false,
    })
  })
})