import { existsSync, rmdirSync, mkdirSync } from 'fs'
import { resolve } from 'path'

import { assertEnv, storage, prominent } from '@lavka-js-toolbox/commands'
import { Bus } from '@yandex-int/ipbus'
import type { KotikConfig, KotikRequest, KotikCacheMeta } from '@yandex-int/kotik'
import { DATA_CTX_ITEM, META_CTX_ITEM } from '@yandex-int/kotik/middleware/regular/constants'
import { pick } from 'lodash'

import { presets, middlewares } from '@lavka/tools/kotik'
import { KOTIK_API, CACHE_MODE_SET_RESULT_BUS_ID, CACHE_KEY_CTX_ID } from '@lavka/tools/kotik/constants'
import { getSource, searchParamsToObject } from '@lavka/tools/kotik/utils'
import { createCacheKey } from '@lavka/tools/kotik/utils/create-cache-key'

import { KOTIK_CACHE_MODE_ID } from '@/commands/constants'

const { TVM_SERVER_URL } = assertEnv('TVM_SERVER_URL')

const IS_DEBUG = process.env.KOTIK_DEBUG_ENABLED === '1'
const DEBUG_LOGS_DIR = resolve(__dirname, 'debug')

if (IS_DEBUG) {
  console.log(prominent('Debug enabled'))
  console.log(prominent(`Debug logs directory:\n${DEBUG_LOGS_DIR}`))
  flushDebugLogs()
}

subscribeCacheModeChanges()

const BLACKBOX_HOST = 'blackbox-test.yandex.net'
const CONFIGS_HOST = 'uconfigs.taxi.tst.yandex.net'
const EXPERIMENTS_HOST = 'experiments3.taxi.tst.yandex.net'
const GAP_HOST = 'grocery-authproxy.lavka.tst.yandex.ru'
const GEOBASE_HOST = 'geobase-test.qloud.yandex.ru'

const sourceFromPath = {
  name: 'sourceFromPath',
  fn: middlewares.sourceFromPath({
    hostnames: {
      [EXPERIMENTS_HOST]: { protocol: 'http' },
      [CONFIGS_HOST]: { protocol: 'http' },
      [GAP_HOST]: { protocol: 'https' },
    },
  }),
}

const debugCacheKeyParams = {
  name: 'debugCacheKeyParams',
  fn: middlewares.debugLog(
    (req) => {
      const { hostname } = getSource(req)
      return resolve(DEBUG_LOGS_DIR, hostname + '.ck.log')
    },
    (req) => {
      const source = getSource(req)
      return {
        type: 'PARAMS',
        originalUrl: req.originalUrl,
        query: searchParamsToObject(source.searchParams),
        body: req.body,
      }
    },
  ),
}

const debugCacheKeyResult = {
  name: 'debugCacheKeyResult',
  fn: middlewares.debugLog(
    (req) => {
      const { hostname } = getSource(req)
      return resolve(DEBUG_LOGS_DIR, hostname + '.ck.log')
    },
    (req) => {
      return {
        type: 'RESULT',
        cacheKey: req.kotik.ctx.get(CACHE_KEY_CTX_ID),
      }
    },
  ),
}

const debugResponse = {
  name: 'debugResponse',
  fn: middlewares.debugLog(
    (req) => {
      const { hostname } = getSource(req)
      return resolve(DEBUG_LOGS_DIR, hostname + '.res.log')
    },
    (req) => {
      const { request, response } = req.kotik.ctx.get<KotikCacheMeta>(META_CTX_ITEM)
      const body = req.kotik.ctx.get(DATA_CTX_ITEM)
      return {
        type: 'RESPONSE',
        request: pick(request, 'url', 'method', 'headers'),
        response,
        body,
      }
    },
  ),
}

const config: KotikConfig = {
  routes: [
    // сработает первый вернувший `true` matcher

    {
      matcher: (req: KotikRequest) => req.originalUrl.startsWith('/favicon.ico'),
      handler: presets.favicon(),
    },
    {
      matcher: (req: KotikRequest) => req.originalUrl.startsWith('/' + KOTIK_API.PREPARE_SUITE),
      handler: presets.prepareSuite(),
    },
    {
      matcher: (req: KotikRequest) => req.originalUrl.startsWith('/tvm/'),
      handler: presets.cachingProxy().addFirst({ name: 'tvmSource', fn: middlewares.tvmSource(TVM_SERVER_URL) }),
    },

    // для `/v1/typed_experiments` делаем свой ключ кэша
    {
      matcher: ({ originalUrl }) =>
        originalUrl.startsWith(`/${EXPERIMENTS_HOST}/v1/typed_experiments`) ||
        originalUrl.startsWith(`/${EXPERIMENTS_HOST}/v1/typed_configs`),
      handler: () => {
        const cachingProxy = presets
          .cachingProxy()
          .addFirst(sourceFromPath)
          .addAfter('cacheKey', {
            name: 'setCacheKey',
            fn: (req, _res, next) => {
              req.kotik.ctx.set(CACHE_KEY_CTX_ID, createCacheKey(req, { getBody: () => '' }))
              next()
            },
          })

        if (IS_DEBUG) {
          cachingProxy
            .addAfter('cachePath', debugCacheKeyParams)
            .addAfter('setCacheKey', debugCacheKeyResult)
            .addAfter('fetch', debugResponse)
        }

        return cachingProxy
      },
    },

    // делаем свой ключ кэша для blackbox ручек
    {
      matcher: ({ originalUrl }) => originalUrl.startsWith(`/${BLACKBOX_HOST}/`),
      handler: () => {
        const cachingProxy = presets
          .cachingProxy()
          .addFirst(sourceFromPath)
          .addAfter('cacheKey', {
            name: 'setCacheKey',
            fn: (req, _res, next) => {
              req.kotik.ctx.set(
                CACHE_KEY_CTX_ID,
                createCacheKey(req, {
                  getQuery: (_req, searchParams) => {
                    const out = new URLSearchParams()
                    const method = searchParams.get('method')
                    if (method !== 'sessionid') {
                      throw new Error(`Unknown blackbox method: "${method}"`)
                    }
                    out.set('method', method)
                    return out
                  },
                }),
              )
              next()
            },
          })

        if (IS_DEBUG) {
          cachingProxy
            .addAfter('cachePath', debugCacheKeyParams)
            .addAfter('setCacheKey', debugCacheKeyResult)
            .addAfter('fetch', debugResponse)
        }

        return cachingProxy
      },
    },

    // для `/v1/get_traits_by_ip` фиксируем ip
    {
      matcher: ({ originalUrl }) => originalUrl.startsWith(`/${GEOBASE_HOST}/v1/get_traits_by_ip`),
      handler: () => {
        const cachingProxy = presets.cachingProxy().addFirst([
          sourceFromPath,
          {
            name: 'setGeobaseIp',
            fn: (req, _res, next) => {
              const source = getSource(req)
              source.searchParams.set('ip', '2a02:6b8:c04:17a:0:522:59e8:6a63')
              next()
            },
          },
        ])

        if (IS_DEBUG) {
          cachingProxy
            .addAfter('cachePath', debugCacheKeyParams)
            .addAfter('cacheKey', debugCacheKeyResult)
            .addAfter('fetch', debugResponse)
        }

        return cachingProxy
      },
    },

    // остальные ручки
    {
      matcher: () => true,
      handler: () => {
        const cachingProxy = presets.cachingProxy().addFirst(sourceFromPath)

        if (IS_DEBUG) {
          cachingProxy
            .addAfter('cachePath', debugCacheKeyParams)
            .addAfter('cacheKey', debugCacheKeyResult)
            .addAfter('fetch', debugResponse)
        }

        return cachingProxy
      },
    },
  ],
}

module.exports = config

function subscribeCacheModeChanges() {
  const storeCacheMode = (inp: unknown) => {
    const cacheMode = Buffer.isBuffer(inp) ? inp.toString() : String(inp)
    console.log(prominent(`Cache mode has been changed to "${cacheMode}"`))
    storage.setSync(KOTIK_CACHE_MODE_ID, cacheMode)
  }

  Bus.create()
    .then((bus) => bus.subscribe(CACHE_MODE_SET_RESULT_BUS_ID, storeCacheMode))
    .catch(console.error)
}

function flushDebugLogs() {
  if (existsSync(DEBUG_LOGS_DIR)) {
    rmdirSync(DEBUG_LOGS_DIR, { recursive: true })
  }

  mkdirSync(DEBUG_LOGS_DIR)
}
