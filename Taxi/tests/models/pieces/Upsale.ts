import type { TestDefinitionCallbackCtx } from 'hermione'

import type { AssertImageOptions } from '@lavka/tests'
import { Browser, mkTestId } from '@lavka/tests'

export class Upsale extends Browser {
  protected readonly rootId = mkTestId('upsale')

  constructor(ctx: TestDefinitionCallbackCtx) {
    super(ctx)
  }

  get selector() {
    return `${this.rootId}`
  }

  waitAndClickRightButton() {
    this.browser.waitForElementAndClick(`${this.rootId} ${mkTestId('right-arrow')}`)
  }
  waitAndClickLeftButton() {
    this.browser.waitForElementAndClick(`${this.rootId} ${mkTestId('left-arrow')}`)
  }

  async assertImage(options?: AssertImageOptions) {
    await this.browser.assertImage(this.rootId, options)
  }
}
