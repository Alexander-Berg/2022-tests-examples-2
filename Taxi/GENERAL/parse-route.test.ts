import { BaseRequest } from 'types/ssr'

import { parseRoute } from './parse-route'

const HOST = 'lavka.yandex.ru'
const HOSTNAME = 'lavka.yandex.ru'
const PROTOCOL = 'https'

const cases = [
  {
    url: '/category-group/1/category/2?subcategory=3&softScroll=true#3',
    result: {
      fullUrl: '/category-group/1/category/2?subcategory=3&softScroll=true#3',
      url: '/category-group/1/category/2?subcategory=3&softScroll=true#3',
    },
  },
  {
    url: '/en-fr/category-group/c2567791951e4b66b0e53c8d93933473/category/607065e388e647829e538fdf086df939?subcategory=5553c28f3a1e458392c1d01d2afb95be000100010001&softScroll=true#5553c28f3a1e458392c1d01d2afb95be000100010001',
    result: {
      locale: {
        lang: 'en',
        region: 'FR',
      },
      fullUrl:
        '/en-fr/category-group/c2567791951e4b66b0e53c8d93933473/category/607065e388e647829e538fdf086df939?subcategory=5553c28f3a1e458392c1d01d2afb95be000100010001&softScroll=true#5553c28f3a1e458392c1d01d2afb95be000100010001',
      url: '/category-group/c2567791951e4b66b0e53c8d93933473/category/607065e388e647829e538fdf086df939?subcategory=5553c28f3a1e458392c1d01d2afb95be000100010001&softScroll=true#5553c28f3a1e458392c1d01d2afb95be000100010001',
    },
  },
  {
    url: '/?foo=bar',
    result: {
      fullUrl: '/?foo=bar',
      url: '/?foo=bar',
    },
  },
  {
    url: '/en-fr/?foo=bar',
    result: {
      locale: {
        lang: 'en',
        region: 'FR',
      },
      fullUrl: '/en-fr/?foo=bar',
      url: '/?foo=bar',
    },
  },
  {
    url: '/en-fr?foo=bar',
    result: {
      locale: {
        lang: 'en',
        region: 'FR',
      },
      fullUrl: '/en-fr?foo=bar',
      url: '/?foo=bar',
    },
  },
  {
    url: '/en-fra/?foo=bar#myhash',
    result: {
      fullUrl: '/en-fra/?foo=bar#myhash',
      url: '/en-fra/?foo=bar#myhash',
    },
  },
  {
    url: '/en-fra/#?foo=bar#myhash',
    result: {
      fullUrl: '/en-fra/#?foo=bar#myhash',
      url: '/en-fra/#?foo=bar#myhash',
    },
  },
  {
    url: '/ru-sr',
    result: {
      fullUrl: '/ru-sr',
      url: '/ru-sr',
    },
  },
  {
    url: '/',
    result: {
      fullUrl: '/',
      url: '/',
    },
  },
  {
    url: '/123',
    result: {
      city: 123,
      fullUrl: '/123',
      url: '/',
    },
  },
  {
    url: '/123/category-group/1/category/2',
    result: {
      city: 123,
      fullUrl: '/123/category-group/1/category/2',
      url: '/category-group/1/category/2',
    },
  },
  {
    url: '/en-fr/123/cart',
    result: {
      city: 123,
      locale: {
        lang: 'en',
        region: 'FR',
      },
      fullUrl: '/en-fr/123/cart',
      url: '/cart',
    },
  },
  {
    url: '/en-fra/123/cart',
    result: {
      fullUrl: '/en-fra/123/cart',
      url: '/en-fra/123/cart',
    },
  },
  {
    url: '/en-sr/123/cart',
    result: {
      fullUrl: '/en-sr/123/cart',
      url: '/en-sr/123/cart',
    },
  },
  {
    url: '/123/ru-ru/cart',
    result: {
      fullUrl: '/123/ru-ru/cart',
      url: '/123/ru-ru/cart',
    },
  },
]

function createRequestMock(url: string): BaseRequest {
  const req = {} as unknown as BaseRequest

  req.headers = { host: HOST }
  req.hostname = HOSTNAME
  req.originalUrl = url
  req.protocol = PROTOCOL

  return req
}

let locationMock: Location | undefined

function patchBrowserLocation(url: string): void {
  locationMock = window.location

  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  delete window.location

  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  window.location = new URL(url, `${PROTOCOL}://${HOST}`)
}

function restoreBrowserLocation(): void {
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  window.location = locationMock
}

describe('getPageEnv/parseRoute', () => {
  for (const testCase of cases) {
    describe(testCase.url, () => {
      test('nodejs', () => {
        const req = createRequestMock(testCase.url)

        // test with request
        const result = parseRoute(req)
        expect(result).toEqual(testCase.result)
      })

      test('browser', () => {
        patchBrowserLocation(testCase.url)

        // test with browser environment
        const result = parseRoute(undefined)
        expect(result).toEqual(testCase.result)

        restoreBrowserLocation()
      })
    })
  }
})
