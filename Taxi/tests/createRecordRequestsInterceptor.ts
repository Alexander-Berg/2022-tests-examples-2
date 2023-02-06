interface Options<T> {
  getUrl: (value: T) => string | undefined
  getMethod: (value: T) => string | undefined
  getData: (value: T) => unknown
}

export interface RequestStackItem {
  data: unknown
  url: string
  calledCount: number
  method: string
}

export const createRecordRequestsInterceptor = <T>({getUrl, getMethod, getData}: Options<T>) => {
  if (!window.requestsStack) {
    window.requestsStack = []
  }
  const uniqRequests = new Map<string, {calledCount: number}>()

  const interceptor = (config: T) => {
    const method = getMethod(config)
    const url = getUrl(config)
    const data = getData(config)

    if (!url || !method) {
      return config
    }

    if (url && window.requestsStack) {
      const reqHash = `${url}:${method}`

      const lastRequestsData = uniqRequests.get(reqHash)
      let nextRequestsData: {calledCount: number} = lastRequestsData ?? {calledCount: 1}
      if (lastRequestsData) {
        nextRequestsData = {...nextRequestsData, calledCount: nextRequestsData.calledCount + 1}
      }

      uniqRequests.set(reqHash, nextRequestsData)
      window.requestsStack.push({
        data,
        url,
        calledCount: nextRequestsData.calledCount,
        method,
      })
    }

    return config
  }

  return interceptor
}

declare global {
  interface Window {
    requestsStack?: Array<RequestStackItem>
  }
}
