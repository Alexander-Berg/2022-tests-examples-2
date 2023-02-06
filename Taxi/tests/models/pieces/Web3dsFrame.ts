import {TestDefinitionCallbackCtx} from 'hermione'

import {Browser, mkDataLoading, mkTestId} from '@lavka/tests'

export class Web3dsFrame extends Browser {
  protected readonly rootId = mkTestId('web-3ds-frame')

  constructor(ctx: TestDefinitionCallbackCtx) {
    super(ctx)
  }

  get selector() {
    return this.rootId
  }

  async waitForLoaded() {
    await this.browser.waitForElementExists(`${this.selector}${mkDataLoading('loaded')}`)
  }
}
