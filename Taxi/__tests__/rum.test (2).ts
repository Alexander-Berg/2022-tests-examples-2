import {Request} from 'express'

import {getPageName} from '../utils'

// для типов
const getReq = (maybeReq: Partial<Request>) => maybeReq as Request

describe('rum', () => {
  describe('utils', () => {
    describe('getPageName', () => {
      it('choose first overlap', () => {
        const urls = {
          MainPage: '/main',
          CategoryPage: '/main',
          CartPage: '/main',
        }
        const req = getReq({
          path: '/main',
        })

        expect(getPageName(req, urls)).toBe('MainPage')
      })
      it('works without leading slash', () => {
        const urls = {
          CheckoutPage: 'checkout',
        }
        const req = getReq({
          path: '/checkout',
        })

        expect(getPageName(req, urls)).toBe('CheckoutPage')
      })
      it('returns NotFoundPage name if nothing was matched', () => {
        const urls = {
          CheckoutPage: 'checkout',
        }
        const req = getReq({
          path: '/olala',
        })

        expect(getPageName(req, urls)).toBe('NotFoundPage')
      })
    })
  })
})
