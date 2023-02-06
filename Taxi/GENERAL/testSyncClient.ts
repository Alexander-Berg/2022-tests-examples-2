import {authProxyUrls, ClientFunction, ProxyApiHeader} from '../src'
import {noop} from '../src'

export const proxyPath = (path: string) => `/${path}`
export const apiPath = (path: string) => `//${path}`

const authResponses = {
  [proxyPath(authProxyUrls.token)]: {
    sk: 'csrf-token',
  },
  [proxyPath(authProxyUrls.startup)]: {
    result: 'fake auth',
  },
}
const header = {
  [ProxyApiHeader.USER_ID]: 'user',
}

export const testSyncClient = (extendedResponses: any): ClientFunction => (options) => {
  const {
    url,
    onSuccess,
  } = options
  const responses = {
    ...authResponses,
    ...extendedResponses,
  }

  if (onSuccess) {
    onSuccess(responses[url], header)
  }

  return noop
}
