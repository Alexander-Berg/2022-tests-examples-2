const fakeStore = {
  actionsDispatched: [] as RStore.Action<any>[],
  actionsProceededToNext: [] as RStore.Action<any>[],
  returnValues: {} as {[action: string]: any},
  state: {} as any,
  onNext: undefined as any,

  reset: () => {
    fakeStore.actionsDispatched = []
    fakeStore.actionsProceededToNext = []
    fakeStore.returnValues = {}
    fakeStore.state = {}
    fakeStore.onNext = undefined
  },

  setOnNext: (onNext: (action: RStore.Action<any>) => void) => {
    fakeStore.onNext = onNext
  },

  setReturnValues (values: any) {
    fakeStore.returnValues = values
  },

  setState (state: any) {
    fakeStore.state = state
  },

  dispatch: (action: RStore.Action<any>) => {
    fakeStore.actionsDispatched.push(action)
    if (fakeStore.returnValues.hasOwnProperty(action.type)) {
      if (typeof fakeStore.returnValues[action.type] === 'function') {
        return fakeStore.returnValues[action.type](action)
      }
      return fakeStore.returnValues[action.type]
    }
    return action
  },

  next (action: RStore.Action<any>) {
    fakeStore.actionsProceededToNext.push(action)
    if (fakeStore.onNext) {
      fakeStore.onNext(action)
    }
  },

  getState () {
    return fakeStore.state
  },
}

export default fakeStore
