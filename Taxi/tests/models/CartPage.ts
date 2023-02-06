import {mkTestId} from '@lavka/tests'

import {BasePage, OpenPageOptions} from './BasePage'

export class CartPage extends BasePage {
  async openPage(options: OpenPageOptions) {
    await this.open('/cart', options)
    await this.waitForPageLoaded()
  }

  async waitForPageLoaded() {
    await this.browser.waitForElementExists(mkTestId('cart-page-layout'))
  }

  async assertImage(options?: {state: string}) {
    await this.browser.assertImage(mkTestId('cart-page-layout'), options)
  }
}
