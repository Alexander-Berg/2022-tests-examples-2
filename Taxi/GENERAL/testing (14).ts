import { AppConfig } from '@yandex-int/yandex-cfg'

import { AUTH_PROXY_TEST_SERVER_URL } from './csp/presets/authProxy'
import { AVATARS_TEST_SERVER_URL } from './csp/presets/avatars'
import { HELP_TAXI_TEST_SERVER_URL, HELP_TAXI_YANGO_TEST_SERVER_URL } from './csp/presets/helpTaxi'
import { SSO_TEST_PASSPORT_URL, SSO_TEST_YANGO_URL } from './csp/presets/passport'
import { TRUST_TEST_SERVER_URL, TRUST_TEST_YANGO_SERVER_URL } from './csp/presets/trust'
import { presets as cspPresets } from './csp/unstable'

const config: AppConfig = {
  csp: {
    project: 'lavkaweb_test',
    presets: cspPresets,
  },
  tvm: {
    clientId: 'tvmlavkagroceryfrontendstandalonetesting',
  },
  blackbox: {
    api: 'http://blackbox-test.yandex.net',
  },
  bunker: {
    api: 'http://bunker-api-dot.yandex.net/v1',
    project: 'lavkaweb/testing',
    version: 'latest',
    updateInterval: 5000,
  },
  passport: {
    serverUrl: {
      yandex: 'https://passport-test.yandex.ru',
      yango: 'https://passport-test.yandex.com',
    },
    tvmDestination: 'passport-test',
    mda2: {
      jsSdk: 'https://sso.tst.yango.com/st/js/v1/mda2.1.min.js',
      root: SSO_TEST_PASSPORT_URL,
      sso: SSO_TEST_YANGO_URL,
    },
  },
  authProxy: {
    serverUrl: AUTH_PROXY_TEST_SERVER_URL,
  },
  trust: {
    serverUrl: {
      yandex: TRUST_TEST_SERVER_URL,
      yango: TRUST_TEST_YANGO_SERVER_URL,
    },
    publicKey:
      'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA5i+9gXgNJbAKus8ltkwfBi33a/KwVvxsiILsrtoY/OQo2MJqBJZs0zJABGGGfEnQ3W1BP16nFeRwnTLBOOH8D6fGHqjSFkwI9b95YsbjPe58UcAUkhKj5j3+gVywTzKkvDtURrFIrF7FjQY8ucfHgA49N1Dac/5r436dmDrnbUGNtxkCWW9mlvnbaWfN9kMf/xK7JzAzDbJz9myZNTAir+y97vVxrXFPbyo5EKbWrtXYMwYsu0yjJckeYcG4SkGD3xvjgJs16mbq6KJM5HMoKRuBWVoJ61+RLHJJ5DhqiPKvMa7s+7i17kyrJu91ZfOWZ0WRFHJOAx3PfK/TgVbA8wIDAQAB',
  },
  experiments: {
    serverUrl: 'http://experiments3.taxi.tst.yandex.net',
  },
  geobase: {
    serverUrl: 'http://geobase-test.qloud.yandex.ru',
  },
  supportChat: {
    serverUrl: {
      yandex: HELP_TAXI_TEST_SERVER_URL,
      yango: `${HELP_TAXI_YANGO_TEST_SERVER_URL}/help`,
    },
  },
  avatars: {
    host: AVATARS_TEST_SERVER_URL,
  },
  rum: {
    project: 'lavkaweb_test',
  },
  market: {
    domain: 'market.lavka.tst.yandex.ru',
  },
  images: {
    newUrl: 'https://avatars.mdst.yandex.net/get-grocery-goods',
    oldUrl: 'https://images.tst.grocery.yandex.net',
    url: 'https://tc.tst.mobile.yandex.net',
  },
  domain: {
    stable: {
      lavka: 'grocery-frontend-standalone.lavka.tst.yandex.ru',
      yango: 'deli.tst.yango.com',
      market: 'market.lavka.tst.yandex.ru',
      yangoYandex: 'deli.tst.yango.yandex.com',
    },
  },

  // для нагрузочного тестирования отдаем по http
  ...(process.env.LOAD_TESTING === '1' ? { uatraits: { useHttp: true } } : {}),
}

module.exports = config
