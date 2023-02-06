import {TestDefinitionCallbackCtx} from 'hermione'

import {Browser, mkTestId, TypeIntoOptions} from '@lavka/tests'

export class NewCardBottomSheet extends Browser {
  protected readonly rootId = mkTestId('wallet-new-card-bottom-sheet')

  constructor(ctx: TestDefinitionCallbackCtx) {
    super(ctx)
  }

  get selector() {
    return this.rootId
  }

  async waitForExists() {
    await this.browser.waitForElementExists(this.selector)
  }

  async clickSubmit() {
    await this.browser.waitForElementAndClick(`${this.selector} ${mkTestId('submit-new-card-button')}`)
  }

  async typeTextToField(fieldName: string, text: string, options?: TypeIntoOptions) {
    await this.browser.typeText(`${this.selector} ${mkTestId(fieldName)}`, text, options)
  }
}
