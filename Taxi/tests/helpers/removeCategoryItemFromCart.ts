import {TestDefinitionCallbackCtx} from 'hermione'

import {mkTestId} from '../utils/mkTestId'

interface Params {
  productId: string
}

export async function removeCategoryItemFromCart(ctx: TestDefinitionCallbackCtx, {productId}: Params) {
  await ctx.browser.waitForElementAndClick(
    [mkTestId('products-list-layout'), mkTestId(`product-id-${productId}`), mkTestId('remove-spin-button')].join(' '),
  )
}
