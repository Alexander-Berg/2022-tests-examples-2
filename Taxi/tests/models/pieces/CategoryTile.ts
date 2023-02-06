import type { TestDefinitionCallbackCtx } from 'hermione'

import type { WaitForElementAndClickOptions } from '@lavka/tests'
import { Browser, mkDataItemId, mkTestId } from '@lavka/tests'

interface Props {
  categoryId: string
}

export class CategoryTile extends Browser {
  protected readonly rootId = mkTestId('tile')
  protected readonly categoryId: string

  constructor(ctx: TestDefinitionCallbackCtx, props: Props) {
    super(ctx)
    this.categoryId = mkDataItemId(props.categoryId)
  }

  get selector() {
    return `${this.rootId}${this.categoryId}`
  }

  async waitAndClick(options?: WaitForElementAndClickOptions) {
    await this.browser.waitForElementAndClick(this.selector, options)
  }
}
