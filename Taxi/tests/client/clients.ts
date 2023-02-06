import {I18nApi} from '@lavka/i18n'
import {ordersClient, cartClient, geoClient, commonClient} from '@lavka/providers'

import {defaultRequestFn} from './default-request-fn'

const i18nApi = {
  i18n: () => '',
  i18nCheck: () => true,
  i18nRaw: () => '',
  lang: () => 'ru',
} as unknown as I18nApi

cartClient.initializeClient({
  requestFn: defaultRequestFn,
  i18nApi,
  maxResolvedConflictCount: Number.MAX_SAFE_INTEGER,
  shouldEnrichCart: false,
})

ordersClient.initializeClient({
  requestFn: defaultRequestFn,
  i18nApi,
})

geoClient.initializeClient({
  requestFn: defaultRequestFn,
  i18nApi,
})

commonClient.initializeClient({
  requestFn: defaultRequestFn,
  i18nApi,
})

export default {
  testCartClient: cartClient,
  testOrdersClient: ordersClient,
  testGeoClient: geoClient,
  testCommonClient: commonClient,
}
