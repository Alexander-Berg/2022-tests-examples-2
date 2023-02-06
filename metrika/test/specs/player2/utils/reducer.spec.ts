import createReducer from '@player2/utils/reducer'

describe('Reducer creator', () => {
  interface State {
    a: string,
    b: number,
  }

  it('Should return initial state properly', () => {
    const initialState = createReducer<State>(
      {},
      {a: 'string', b: 123})(undefined, {type: 'init', payload: null} as any
    )

    expect(initialState).toEqual({a: 'string', b: 123})
  })

  it('Should update state properly', () => {
    const actionType = 'someType'
    const initialState = {a: 'string', b: 0}
    const reducer = createReducer<State>({
      [actionType]: (
        prevState: State,
        action: RStore.Action<number>
      ) => ({
        ...prevState,
        b: prevState.b + action.payload,
      }),
    }, initialState)

    let state = reducer(undefined, {
      type: 'init',
      payload: null,
    } as RStore.Action<any>)

    state = reducer(state, {
      type: actionType,
      payload: 3,
    } as RStore.Action<any>)

    state = reducer(state, {
      type: actionType,
      payload: 4,
    } as RStore.Action<any>)

    expect(state).toEqual({a: 'string', b: 7})
  })
})
