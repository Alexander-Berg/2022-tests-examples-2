import {createQueryClient} from '../../src/query-client'

import './clients'

export function createTestQueryClient() {
  return createQueryClient({
    retry: 0,
    cacheTime: Infinity,
  })
}
