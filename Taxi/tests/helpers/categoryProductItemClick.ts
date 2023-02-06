import type {TestDefinitionCallbackCtx} from 'hermione'

import {mkTestId} from '../utils/mkTestId'

interface Params {
  productId: string
}

export async function categoryProductItemClick(ctx: TestDefinitionCallbackCtx, {productId}: Params) {
  await ctx.browser.waitForElementAndClick(
    [mkTestId('products-list-layout'), mkTestId(`product-id-${productId}`)].join(' '),
  )
}
