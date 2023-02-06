import fetch, {RequestInit} from 'node-fetch'

import {createApi, Result, StaticApiOptions} from '../src/createApi'

jest.mock('node-fetch')
const {Response} = jest.requireActual('node-fetch')
const mockedFetch = fetch as jest.MockedFunction<typeof fetch>

afterEach(() => {
  mockedFetch.mockClear()
  mockedFetch.mockReset()
})

const fixedJsonData = {
  fixedData: 'fixedData',
}

test('createApi()', async () => {
  mockedFetch.mockReturnValueOnce(Promise.resolve(new Response('')))

  const api = createApi('')
  const result = await api.get('/')

  expect(result.status).toBe('OK')
})

test('get()', async () => {
  mockedFetch.mockReturnValueOnce(new Response(JSON.stringify(fixedJsonData)))
  const api = createApi('')
  const result = await api.get('/')

  expect(mockedFetch).toHaveBeenCalledTimes(1)
  expect(result.status).toBe('OK')
  if (result.status === 'OK') {
    const response = result.data
    expect(response.ok).toBe(true)
    if (response.ok) {
      expect(response.data).toEqual(fixedJsonData)
    }
  }
})

test('post()', async () => {
  mockedFetch.mockReturnValueOnce(new Response(JSON.stringify(fixedJsonData)))
  const api = createApi('')
  const result = await api.post('/', fixedJsonData)

  expect(mockedFetch).toHaveBeenCalledTimes(1)
  expect(result.status).toBe('OK')
  if (result.status === 'OK') {
    const response = result.data
    expect(response.ok).toBe(true)
    if (response.ok) {
      expect(response.data).toEqual(fixedJsonData)
    }
  }
})

test('TIMEOUT_ERROR', async () => {
  mockedFetch.mockImplementationOnce(async (_url, {signal}: RequestInit = {}) => {
    return new Promise((resolve, reject) => {
      if (signal) {
        signal.onabort = () => {
          reject({
            name: 'AbortError',
            code: 'TIMEOUT_ERROR',
          })
        }
      }

      setTimeout(() => {
        resolve(new Response('{}'))
      }, 50)
    })
  })

  const api = createApi('', {timeout: 1})
  const result = await api.get('/')

  expect(result.status).toBe('ERROR')
  if (result.status === 'ERROR') {
    expect(result.error.code).toBe('TIMEOUT_ERROR')
  }
})

test('PARSE_ERROR', async () => {
  mockedFetch.mockReturnValueOnce(new Response('text'))
  const api = createApi('')
  const result = await api.get('/')

  expect(mockedFetch).toHaveBeenCalledTimes(1)
  expect(result.status).toBe('OK')
  if (result.status === 'OK') {
    const response = result.data
    expect(response.ok).toBe(false)
    if (!response.ok) {
      expect(response.error.code).toBe('PARSE_ERROR')
    }
  }
})

test('URL_MISSING_ERROR', async () => {
  let api = createApi('')
  api.requestInterceptor.use(async options => {
    options.url = ''
    return options
  })
  let result = await api.get('/')

  expect(result.status).toBe('ERROR')
  if (result.status === 'ERROR') {
    expect(result.error.code).toBe('URL_MISSING_ERROR')
  }

  api = createApi()
  result = await api.get('')

  expect(result.status).toBe('ERROR')
  if (result.status === 'ERROR') {
    expect(result.error.code).toBe('URL_MISSING_ERROR')
  }
})

test('NETWORK_ERROR', async () => {
  mockedFetch.mockReturnValueOnce(Promise.reject(new TypeError()))
  const api = createApi(`http://localhosttt`)

  const result = await api.get('/')

  expect(result.status).toBe('ERROR')
  if (result.status === 'ERROR') {
    expect(result.error.code).toBe('NETWORK_ERROR')
  }
})

test('Request Interceptors', async () => {
  mockedFetch.mockReturnValue(new Response('{}'))

  const interceptorCallCounter = {
    count: async (requestOptions: StaticApiOptions) => requestOptions,
  }
  const spy = jest.spyOn(interceptorCallCounter, 'count')

  const api = createApi('')
  api.requestInterceptor.use(interceptorCallCounter.count)
  const second = api.requestInterceptor.use(interceptorCallCounter.count)
  api.requestInterceptor.use(interceptorCallCounter.count)

  let result = await api.get('/')
  expect(mockedFetch).toHaveBeenCalledTimes(1)
  expect(result.status).toBe('OK')
  if (result.status === 'OK') {
    expect(spy).toHaveBeenCalledTimes(3)
  }

  api.requestInterceptor.remove(second)
  result = await api.get('/')
  expect(mockedFetch).toHaveBeenCalledTimes(2)
  expect(result.status).toBe('OK')
  if (result.status === 'OK') {
    expect(spy).toHaveBeenCalledTimes(5)
  }

  spy.mockRestore()
})

test('Response Interceptors', async () => {
  mockedFetch.mockReturnValue(new Response('{}'))
  const interceptorCallCounter = {
    count: async (result: Result) => result,
  }
  const spy = jest.spyOn(interceptorCallCounter, 'count')

  const api = createApi('')

  api.responseInterceptor.use(interceptorCallCounter.count)
  const second = api.responseInterceptor.use(interceptorCallCounter.count)
  api.responseInterceptor.use(interceptorCallCounter.count)

  let result = await api.get('/')
  expect(mockedFetch).toHaveBeenCalledTimes(1)
  expect(result.status).toBe('OK')
  if (result.status === 'OK') {
    expect(spy).toHaveBeenCalledTimes(3)
  }

  api.responseInterceptor.remove(second)
  result = await api.get('/')
  expect(mockedFetch).toHaveBeenCalledTimes(2)
  expect(result.status).toBe('OK')
  if (result.status === 'OK') {
    expect(spy).toHaveBeenCalledTimes(5)
  }
})
