interface CallbackConfig {
  returns?: any|Function
  async?: boolean
}
interface CallbacksConfig {
  [action: string]: CallbackConfig
}

const defaultConfig: CallbackConfig = {
  returns: undefined,
}

export default class ActionsWrapper {
  private proxiedActions: any = {}
  private actionsCalled: RStore.Action<any>[] = []

  constructor(actions: any, configs: CallbacksConfig = {}) {
    Object.keys(actions).forEach((key: string) => {
      if (typeof actions[key] === 'function') {
        this.proxiedActions[key] = (...args: any[]) => {
          const action = actions[key](...args)
          this.actionsCalled.push(action)
          const config = configs[key] ? configs[key] : defaultConfig
          const result = typeof config.returns === 'function'
            ? config.returns(...args)
            : config.returns

          if (config.async) {
            if (result instanceof Error) {
              return Promise.reject(result)
            } else {
              return Promise.resolve(result)
            }
          }

          return result
        }
      }
    })
  }

  getProxiedActions () {
    return this.proxiedActions
  }

  getCalledActions () {
    return this.actionsCalled
  }

  clear () {
    this.actionsCalled = []
  }
}
