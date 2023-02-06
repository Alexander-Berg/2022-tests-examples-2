import qs from 'querystring'

import {mkTestId} from '@lavka/tests'

import {BasePage, OpenPageOptions} from './BasePage'

export class HourSlotsCheckoutPage extends BasePage {
  async openPage(query: {packageOrder: string}, options: OpenPageOptions) {
    await this.open('/hour-slots-checkout/?' + qs.stringify(query), options)
  }

  async waitForPageLoaded() {
    await this.browser.waitForElementExists(mkTestId('hour-slots-checkout-page-layout'))
  }

  async assertImage(options?: {state: string}) {
    await this.browser.assertImage(mkTestId('hour-slots-checkout-page-layout'), options)
  }
}
