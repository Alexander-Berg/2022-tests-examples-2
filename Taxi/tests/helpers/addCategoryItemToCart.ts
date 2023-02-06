import type {TestDefinitionCallbackCtx} from 'hermione'

import {mkTestId} from '../utils/mkTestId'

interface Params {
  productId: string
  firstAddition?: boolean
}

export async function addCategoryItemToCart(ctx: TestDefinitionCallbackCtx, {productId, firstAddition}: Params) {
  await ctx.browser.waitForElementAndClick(
    [
      mkTestId('products-list-layout'),
      mkTestId(`product-id-${productId}`),
      firstAddition ? mkTestId('product-card-add-button') : mkTestId('add-spin-button'),
    ].join(' '),
  )
}
