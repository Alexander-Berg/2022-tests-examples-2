import qs from 'querystring'

import {mkDataLoading, mkTestId} from '@lavka/tests'

import {BasePage, OpenPageOptions} from './BasePage'
import {Upsale} from './pieces'

export class OneClickCheckoutPage extends BasePage {
  async openPage(query: {packageOrder: string}, options: OpenPageOptions) {
    await this.open('/one-click-checkout/?' + qs.stringify(query), options)
  }

  async waitForPageLoaded() {
    await this.browser.waitForElementExists(mkTestId('one-click-checkout-page-layout'))
  }

  async waitForUpsaleLoaded() {
    await this.browser.waitForElementExists(
      `${mkTestId('one-click-checkout-page-layout')} ${mkTestId('product-upsale')}${mkDataLoading('false')}`,
    )
  }

  async assertImage(options?: {state: string}) {
    await this.browser.assertImage(mkTestId('one-click-checkout-page-layout'), options)
  }

  async assertPageItemSubtitle(text: string) {
    await this.browser.waitForElementText(mkTestId('delivery-cart-package-item-subtitle'), text)
  }

  getUpsale() {
    return new Upsale(this.ctx, 'product-upsale')
  }
}
