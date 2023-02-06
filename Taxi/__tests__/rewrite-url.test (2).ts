import {parseUrl} from '../utils'

describe('rewrite-url', () => {
  describe('for GAP', () => {
    it('works for different environments', () => {
      const parsedProd = parseUrl('/4.0/grocery-superapp/lavka', false)
      const parsedNamedStand = parseUrl('/4.0/grocery-superapp-testing/lavka', false)
      const parsedPrStandLegacy = parseUrl('/4.0/grocery-superapp-proxy/777/lavka', false)
      const parsedPrStand = parseUrl('/4.0/grocery-superapp/dev-stand-pr/777/lavka', false)
      const parsedAnyStand = parseUrl('/4.0/grocery-superapp/v3new/lavka', false)

      expect(parsedProd.baseURL).toBe('/4.0/grocery-superapp/')
      expect(parsedNamedStand.baseURL).toBe('/4.0/grocery-superapp-testing/')
      expect(parsedPrStandLegacy.baseURL).toBe('/4.0/grocery-superapp-proxy/777/')
      expect(parsedPrStand.baseURL).toBe('/4.0/grocery-superapp/dev-stand-pr/777/')
      expect(parsedAnyStand.baseURL).toBe('/4.0/grocery-superapp/v3new/')
    })
    it('catches rest of url', () => {
      const parsedProd = parseUrl('/4.0/grocery-superapp/lavka/my/super/checkout', false)
      const parsedNamedStand = parseUrl('/4.0/grocery-superapp-testing/lavka/my/super/checkout', false)
      const parsedPrStandLegacy = parseUrl('/4.0/grocery-superapp-proxy/777/lavka/my/super/checkout', false)
      const parsedPrStand = parseUrl('/4.0/grocery-superapp/dev-stand-pr/777/lavka/my/super/checkout', false)
      const parsedAnyStand = parseUrl('/4.0/grocery-superapp/v3new/lavka/my/super/checkout', false)

      expect(parsedProd.reqUrl).toBe('/my/super/checkout')
      expect(parsedNamedStand.reqUrl).toBe('/my/super/checkout')
      expect(parsedPrStandLegacy.reqUrl).toBe('/my/super/checkout')
      expect(parsedPrStand.reqUrl).toBe('/my/super/checkout')
      expect(parsedAnyStand.reqUrl).toBe('/my/super/checkout')
    })
    it('do not catch too long nesting', () => {
      const parsed = parseUrl('/4.0/grocery-superapp/very/long/nesting/lavka', false)

      expect(parsed.matched).toBeFalsy()
    })
  })

  describe('for EAP', () => {
    it('works for different environments', () => {
      const parsedProd = parseUrl('/eats/v1/grocery-superapp/lavka', true)
      const parsedNameStand = parseUrl('/eats/v1/grocery-superapp-testing/lavka', true)
      const parsedAnyStand = parseUrl('/eats/v1/grocery-superapp/v3new/lavka', true)

      expect(parsedProd.baseURL).toBe('/eats/v1/grocery-superapp/')
      expect(parsedNameStand.baseURL).toBe('/eats/v1/grocery-superapp-testing/')
      expect(parsedAnyStand.baseURL).toBe(undefined)
    })
    it('catches rest of url', () => {
      const parsedProd = parseUrl('/eats/v1/grocery-superapp/lavka/my/super/checkout', true)
      const parsedNamedStand = parseUrl('/eats/v1/grocery-superapp-testing/lavka/my/super/checkout', true)
      const parsedAnyStand = parseUrl('/eats/v1/grocery-superapp/v3new/lavka/my/super/checkout', true)

      expect(parsedProd.reqUrl).toBe('/my/super/checkout')
      expect(parsedNamedStand.reqUrl).toBe('/my/super/checkout')
      expect(parsedAnyStand.reqUrl).toBe(undefined)
    })
  })
})
