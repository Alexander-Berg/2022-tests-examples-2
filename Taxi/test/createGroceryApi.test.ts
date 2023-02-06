import fetch, {RequestInit} from 'node-fetch'

import {StaticApiOptions} from '../src/createApi'
import {createGroceryApi, createGroceryApiWithGlobalSettings} from '../src/createGroceryApi'
import {globalSettings} from '../src/globalSettings'

jest.mock('node-fetch')
const {Response} = jest.requireActual('node-fetch')
const mockedFetch = fetch as jest.MockedFunction<typeof fetch>

afterEach(() => {
  mockedFetch.mockClear()
  mockedFetch.mockReset()
})

test('createGroceryApiWithGlobalSettings()', async () => {
  mockedFetch.mockReturnValueOnce(new Response(JSON.stringify('{}')))

  const apiOptions: StaticApiOptions = {}
  const api = createGroceryApiWithGlobalSettings('', apiOptions)
  const result = await api.get('/')
  expect(result.status).toBe('OK')
})

test('createGroceryApi()', async () => {
  mockedFetch.mockReturnValueOnce(new Response(JSON.stringify('{}')))

  const api = createGroceryApi('', globalSettings)
  const result = await api.get('/')
  expect(result.status).toBe('OK')
})

test('ApiOptions merge order', async () => {
  mockedFetch.mockReturnValue(new Response(JSON.stringify('{}')))

  const settings = {
    ...globalSettings,
    retries: 2,
    apiOptions: {
      timeout: 500,
      headers: {'global-header': 'global-header'},
    },
  }

  const api = createGroceryApi('', settings)

  let result = await api.get('/')
  expect(result.status).toBe('OK')
  if (result.status === 'OK') {
    expect(result.data.requestOptions.timeout).toBe(500)
    expect(result.data.requestOptions.headers).toEqual({'global-header': 'global-header'})
  }

  result = await api.get('/', {timeout: 300, headers: {'local-header': 'local-header'}})
  expect(result.status).toBe('OK')
  if (result.status === 'OK') {
    expect(result.data.requestOptions.timeout).toBe(300)
    expect(result.data.requestOptions.headers).toEqual({
      'global-header': 'global-header',
      'local-header': 'local-header',
    })
  }
})

test('retries setting', async () => {
  mockedFetch.mockImplementation((_url, {signal}: RequestInit = {}) => {
    return new Promise((resolve, reject) => {
      if (signal) {
        signal.onabort = () =>
          reject({
            name: 'AbortError',
            code: 'TIMEOUT_ERROR',
          })
      }

      setTimeout(() => {
        resolve(new Response('{}'))
      }, 50)
    })
  })

  const settings = {
    ...globalSettings,
    retries: 2,
    apiOptions: {
      timeout: 1,
    },
  }

  const api = createGroceryApi('', settings)
  const result = await api.get('/')

  expect(result.status).toBe('ERROR')
  if (result.status === 'ERROR') {
    expect(result.error.code).toBe('TIMEOUT_ERROR')
    expect(mockedFetch).toHaveBeenCalledTimes(3)
  }
})
