import {TestDefinitionCallbackCtx} from 'hermione'

import {ScrollToElementOptions, Browser, mkTestId} from '@lavka/tests'

export class Upsale extends Browser {
  private readonly selector: string

  constructor(ctx: TestDefinitionCallbackCtx, selector: string) {
    super(ctx)

    this.selector = selector
  }

  private getTestId(id?: string) {
    if (id) {
      return mkTestId(`${this.selector} ${id}`)
    }

    return mkTestId(this.selector)
  }

  async scrollToUpsale(options?: ScrollToElementOptions) {
    await this.browser.scrollToElement(this.getTestId(), options)
  }

  async scrollToRightEdge() {
    await this.browser.scrollToElementEdge(this.getTestId('horizontal-scrollable-container'), {
      direction: 'right',
    })
  }

  async clickAddProductToCart(productId: string) {
    const id = this.getTestId(`${productId} product-card-add-button`)
    await this.browser.waitForElementAndClick(id)
  }

  async clickAddProductSpin(productId: string) {
    const id = this.getTestId(`${productId} add-spin-button`)
    await this.browser.waitForElementAndClick(id)
  }

  async clickRemoveProductSpin(productId: string) {
    const id = this.getTestId(`${productId} remove-spin-button`)
    await this.browser.waitForElementAndClick(id)
  }
}
