import type {TestDefinitionCallbackCtx} from 'hermione'

import {mkTestId} from '../utils/mkTestId'

export async function backHeaderButtonClick(ctx: TestDefinitionCallbackCtx) {
  await ctx.browser.waitForElementAndClick(mkTestId('left-icon'))
}
