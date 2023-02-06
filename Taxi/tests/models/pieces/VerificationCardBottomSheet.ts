import {TestDefinitionCallbackCtx} from 'hermione'

import {Browser, mkTestId, WaitForElementExistsOptions} from '@lavka/tests'

export class VerificationCardBottomSheet extends Browser {
  protected readonly rootId = mkTestId('verification-card-bottom-sheet')

  constructor(ctx: TestDefinitionCallbackCtx) {
    super(ctx)
  }

  get selector() {
    return this.rootId
  }

  async waitForExists(options?: WaitForElementExistsOptions) {
    await this.browser.waitForElementExists(this.selector, options)
  }
}
