import fetch from 'node-fetch'

import {RequestFnContext} from '@lavka/providers'

export const defaultRequestFn = async ({url, method, body, headers}: RequestFnContext) => {
  const host = `http://localhost:7777`
  const prefix = '/4.0/eda-superapp'
  const fullUrl = `${host}${prefix}${url}`

  const res = await fetch(fullUrl, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    body: JSON.stringify(body),
  })

  return await res.json()
}
