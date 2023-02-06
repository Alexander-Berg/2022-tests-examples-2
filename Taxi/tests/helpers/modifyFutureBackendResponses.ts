import {Cookie} from '@wdio/protocols'
import {TestDefinitionCallbackCtx} from 'hermione'

import {PaymentMethod} from '@lavka/api-typings/schemas/api-proxy-superapp-critical/paymentmethods'
import {VerificationStatus} from '@lavka/api-typings/schemas/card-antifraud/api/api'
import {CartResponse, Cashback} from '@lavka/api-typings/uservices/grocery-cart/definitions/common-responses'
import {GroceryOrderPaymentStatus, GroceryOrderResolution} from '@lavka/api-typings/uservices/grocery-orders/api/orders'
import {GroceryOrderStatus} from '@lavka/api-typings/uservices/grocery-orders/definitions'

interface Cart {
  'cart:cashback': CartResponse['cashback']
  'cart:cashback:full_payment': Cashback['full_payment']
  'cart:promocode': CartResponse['promocode']
  'cart:total_price_template': CartResponse['total_price_template']
}

interface ListPaymentMethods {
  'list-payment-methods:last_used_payment_method': PaymentMethod
  'list-payment-methods:payment_methods': PaymentMethod[]
}

interface GetAddress {
  'get-address:comment': string
  'get-address:is_new_address': boolean
}

interface OrdersState {
  'grocery_orders[0]:status': GroceryOrderStatus
  'grocery_orders[0]:resolution': GroceryOrderResolution
  'grocery_orders[0]:payment_status': GroceryOrderPaymentStatus
}

interface CardAntifraud {
  'card-antifraud:status': VerificationStatus
}

type Data = Partial<Cart & GetAddress & ListPaymentMethods & OrdersState & CardAntifraud>

export const makeFutureBackendResponsesCookie = (data: Data) => {
  const result: Record<string, string> = {}
  Object.entries(data).forEach(([key, value]) => {
    result[`response:${key}`] = typeof value === 'object' ? JSON.stringify(value) : String(value)
  })
  return result
}

export const modifyFutureBackendResponses = (ctx: TestDefinitionCallbackCtx, data: Data) => {
  const cookieData: Cookie[] = []

  Object.entries(makeFutureBackendResponsesCookie(data)).forEach(([name, value]) => {
    cookieData.push({value, name})
  })

  ctx.browser.setCookies(cookieData)
}
