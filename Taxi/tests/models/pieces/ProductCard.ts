import type { TestDefinitionCallbackCtx } from 'hermione'

import type { WaitForElementAndClickOptions } from '@lavka/tests'
import { Browser, mkDataItemId, mkTestId } from '@lavka/tests'

interface Props {
  productId: string
}

export class ProductCard extends Browser {
  protected readonly rootId = mkTestId('product-card')
  protected readonly productId: string

  constructor(ctx: TestDefinitionCallbackCtx, props: Props) {
    super(ctx)
    this.productId = mkDataItemId(props.productId)
  }

  get selector() {
    return `${this.rootId}${this.productId}`
  }

  async waitAndClick(options?: WaitForElementAndClickOptions) {
    await this.browser.waitForElementAndClick(this.selector, options)
  }

  async addToCart(options?: { firstItem?: boolean }) {
    if (options?.firstItem) {
      await this.browser.waitForElementAndClick(`${this.selector} ${mkTestId('product-card-add-button')}`)
    } else {
      await this.browser.waitForElementAndClick(`${this.selector} ${mkTestId('add-spin-button')}`)
    }
  }

  async removeProduct() {
    await this.browser.waitForElementAndClick(`${this.selector} ${mkTestId('remove-spin-button')}`)
  }
}
