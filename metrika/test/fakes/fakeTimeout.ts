interface TimoutCallback {
  callback: Function
  time: number
  id: number
}

let timeoutId = 0
let callbacks: TimoutCallback[] = []

export default {
  reset () {
    callbacks = []
    timeoutId = 0
  },

  setTimeout: (callback: Function, time: number = 0) => {
    timeoutId++
    callbacks.push({callback, time, id: timeoutId})

    return timeoutId
  },

  clearTimeout: (idToRemove: number) => {
    callbacks = callbacks.filter(({id}) => id !== idToRemove)
  },

  resolveTimeouts: () => {
    callbacks.sort((a: TimoutCallback, b: TimoutCallback) =>
      a.time - b.time || a.id - b.id
    )
    .forEach(({callback}) => callback())
  },
}