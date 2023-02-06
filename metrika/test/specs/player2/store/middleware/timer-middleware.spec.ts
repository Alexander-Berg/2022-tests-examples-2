import { batchActions } from 'redux-batched-actions'
import timerMiddlewareCreator from '@player2/store/middleware/timer-middleware'
import { tick, rewind, pause, play, setReady, setFinished, PLAY, PAUSE, SET_READY } from '@player2/store/actions/timer'
import { setChangeset } from '@player2/store/actions/projector'
import { processTabsChanges } from '@player2/store/actions/tabs'
import { SELECT_CURRENT_HIT, selectCurrentHit } from '@player2/store/actions/currentHit'
import fakeStore from '@test/fakes/fakeStore'
import fakeTimeout from '@test/fakes/fakeTimeout'

describe('Timer middleware', () => {
  const {setTimeout, clearTimeout} = fakeTimeout
  const middleware = timerMiddlewareCreator(setTimeout, clearTimeout)(fakeStore as any)(fakeStore.next)

  const eventsOrMutations = [
    {stamp: 1},
    {stamp: 2},
    {stamp: 3},
    {stamp: 4},
    {stamp: 5},
  ]
  const defaultState = {
    api: {
      visitInfo: {
        data: {
          tabChanges: [
            {
              type: 'select',
              watchId: 0,
              stamp: 0,
            },
            {
              type: 'select',
              watchId: 0,
              stamp: 1,
            },
            {
              type: 'select',
              watchId: 1,
              stamp: 5,
            },
            {
              type: 'select',
              watchId: 2,
              stamp: 10,
            },
          ],
        },
      },
    },
    currentHit: {
      index: 0,
      duration: 5,
      mutations: eventsOrMutations,
      events: eventsOrMutations,
      stamp: 0,
    },
    timer: {
      time: 1,
      speed: 3,
      playing: false,
      ready: false,
      finished: false,
      rewinding: false,
    },
  }

  it('Handles tick correctly', () => {
    fakeStore.reset()
    fakeTimeout.reset()
    fakeStore.setState(defaultState)
    fakeStore.setOnNext((action: RStore.Action<number>) => {
      fakeStore.setState({
        ...defaultState,
        timer: {
          ...defaultState.timer,
          time: action.payload + defaultState.timer.time,
        },
      })
    })

    const changeset = [
      {stamp: 2},
      {stamp: 3},
      {stamp: 4},
      {stamp: 5},
    ] as any
    middleware(tick(4))
    expect({
      next: fakeStore.actionsProceededToNext,
      dispatch: fakeStore.actionsDispatched,
    }).toEqual({
      next: [tick(4)],
      dispatch: [
        batchActions([
          processTabsChanges([{
            type: 'select',
            watchId: 1,
            stamp: 5,
          }]),
          setChangeset(changeset, changeset),
          setReady(false),
        ]),
      ],
    })
  })

  it('handles rewind correctly', () => {
    fakeStore.reset()
    fakeTimeout.reset()
    fakeStore.setState(defaultState)
    fakeStore.setOnNext((action: RStore.Action<number>) => {
      fakeStore.setState({
        ...defaultState,
        timer: {
          ...defaultState.timer,
          time: action.payload,
        },
      })
    })
    const resultPromise = Promise.resolve()
    fakeStore.setReturnValues({
      [SELECT_CURRENT_HIT]: () => ({
        then: (callback: (hit: any) => void) => resultPromise.then(() => callback({
          index: 2,
          duration: 5,
          mutations: eventsOrMutations,
          events: eventsOrMutations,
          stamp: 5,
        })),
      }),
    })
    middleware(rewind(9))
    const changeset = [
      {stamp: 1},
      {stamp: 2},
      {stamp: 3},
      {stamp: 4},
    ]
    expect(resultPromise.then(() => ({
        next: fakeStore.actionsProceededToNext,
        dispatch: fakeStore.actionsDispatched,
      })))
      .resolves.toEqual({
        next: [rewind(9)],
        dispatch: [
          batchActions([
            setReady(false),
            pause(),
          ]),
          selectCurrentHit(1),
          batchActions([
            processTabsChanges([
              {
                type: 'select',
                watchId: 0,
                stamp: 0,
              },
              {
                type: 'select',
                watchId: 0,
                stamp: 1,
              },
              {
                type: 'select',
                watchId: 1,
                stamp: 5,
              },
            ], true),
            setFinished(false),
            setChangeset(changeset, changeset),
            play(),
          ]),
        ],
      })
  })

  const playPasuseNextCallbacks = (action: RStore.Action<any>) => {
    let state = fakeStore.getState()
    switch (action.type) {
      case PLAY:
        state = {
          ...state,
          timer: {
            ...state.timer,
            playing: true,
          },
        }
        break
      case PAUSE:
        state = {
          ...state,
          timer: {
            ...state.timer,
            playing: false,
          },
        }
        break
      case SET_READY:
        state = {
          ...state,
          timer: {
            ...state.timer,
            ready: action.payload,
          },
        }
        break
      default:
        break
    }
    fakeStore.setState(state)
  }

  it ('handles play, setReady (true) correctly (default behaviour)', () => {
    fakeStore.reset()
    fakeTimeout.reset()
    fakeStore.setState(defaultState)
    fakeStore.setOnNext(playPasuseNextCallbacks)
    middleware(setReady(true))
    fakeTimeout.resolveTimeouts()
    middleware(play())
    fakeTimeout.resolveTimeouts()
    expect({
      next: fakeStore.actionsProceededToNext,
      dispatch: fakeStore.actionsDispatched,
    }).toEqual({
      next: [setReady(true), play()],
      dispatch: [tick(3)],
    })
  })

  it ('handles play, setReady (true) correctly and rewinds', () => {
    fakeStore.reset()
    fakeTimeout.reset()
    fakeStore.setState({
      ...defaultState,
      timer: {
        ...defaultState.timer,
        time: 6,
      },
    })
    fakeStore.setOnNext(playPasuseNextCallbacks)
    middleware(setReady(true))
    fakeTimeout.resolveTimeouts()
    middleware(play())
    fakeTimeout.resolveTimeouts()
    expect({
      next: fakeStore.actionsProceededToNext,
      dispatch: fakeStore.actionsDispatched,
    }).toEqual({
      next: [setReady(true), play()],
      dispatch: [rewind(5), tick(3)],
    })
  })

  it ('handles play, setReady stops at the end', () => {
    fakeStore.reset()
    fakeTimeout.reset()
    fakeStore.setState({
      ...defaultState,
      timer: {
        ...defaultState.timer,
        time: 16,
      },
      currentHit: {
        index: 2,
        duration: 5,
        stamp: 10,
        mutations: eventsOrMutations,
        events: eventsOrMutations,
      },
    })
    fakeStore.setOnNext(playPasuseNextCallbacks)
    middleware(setReady(true))
    fakeTimeout.resolveTimeouts()
    middleware(play())
    fakeTimeout.resolveTimeouts()

    expect({
      next: fakeStore.actionsProceededToNext,
      dispatch: fakeStore.actionsDispatched,
    }).toEqual({
      next: [setReady(true), play()],
      dispatch: [
        batchActions([
          pause(),
          setReady(false),
          setFinished(true),
        ]),
      ],
    })
  })

  it ('handles pause and set ready (false) and stops all timeouts', () => {
    fakeStore.reset()
    fakeTimeout.reset()
    fakeStore.setState({
      ...defaultState,
      timer: {
        ...defaultState.timer,
        playing: true,
      },
    })
    fakeStore.setOnNext(playPasuseNextCallbacks)
    middleware(setReady(true))
    middleware(pause())
    fakeTimeout.resolveTimeouts()
    middleware(play())
    middleware(setReady(false))
    fakeTimeout.resolveTimeouts()

    expect({
      next: fakeStore.actionsProceededToNext,
      dispatch: fakeStore.actionsDispatched,
    }).toEqual({
      next: [setReady(true), pause(), play(), setReady(false)],
      dispatch: [],
    })
  })
})
