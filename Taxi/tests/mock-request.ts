import {promises as fs} from 'fs'
import path from 'path'

import {isObjectLike} from '../src/utils/error'

export function readMockRequest(name: string) {
  let runCount = 0

  return async () => {
    const filepath = path.join(__dirname, 'mocks', name, runCount + '.json')
    runCount++
    const fileContent = await fs.readFile(filepath, {encoding: 'utf8'})
    const res = JSON.parse(fileContent)
    if (hasRequestError(res)) {
      throw new RequestError(res.request_error.status, res.request_error.data)
    }
    return res
  }
}

class RequestError extends Error {
  status: number
  data: unknown

  constructor(status: number, data: unknown) {
    super('request error')
    this.status = status
    this.data = data
  }
}

interface RequestErrorJSON {
  request_error: {
    status: number
    data: unknown
  }
}

function hasRequestError(value: unknown): value is RequestErrorJSON {
  return isObjectLike(value) && 'request_error' in value
}
