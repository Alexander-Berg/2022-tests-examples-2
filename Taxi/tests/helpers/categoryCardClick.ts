import type {TestDefinitionCallbackCtx} from 'hermione'

import {mkTestId} from '../utils/mkTestId'

interface Params {
  categoryId: string
}

export async function categoryCardClick(ctx: TestDefinitionCallbackCtx, {categoryId}: Params) {
  await ctx.browser.waitForElementAndClick(
    [mkTestId('cards-grid'), `${mkTestId(`category-card`)}[data-category-id="${categoryId}"]`].join(' '),
  )
}
