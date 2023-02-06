import {mkDataValue, mkTestId} from '@lavka/tests'

import {BasePage} from './BasePage'

export class BundleBottomSheet extends BasePage {
  async waitForExists() {
    await this.browser.waitForElementExists(mkTestId('bundle-bottom-sheet'))
  }

  async assertImage(options?: {state: string}) {
    await this.browser.assertImage(mkTestId('bundle-bottom-sheet'), options)
  }

  async clickReplaceButton(index: number) {
    await this.browser.waitForElementAndClick(mkTestId(`bundle-item-${index} bundle-replace-button`))
  }

  async selectBundlePart(id: string) {
    await this.browser.waitForElementAndClick(
      `${mkTestId('bundle-replace-bottom-sheet')} ${mkDataValue(id)} ${mkTestId('product-card')}`,
    )
  }

  async confirmBundleReplace() {
    await this.browser.waitForElementAndClick(
      `${mkTestId('bundle-replace-bottom-sheet')}  ${mkTestId('bundle-replace-confirm')}`,
    )
  }

  async waitTillPriceIs(price: number) {
    await this.browser.waitForElementText(mkTestId('bundle-bottom-sheet add-to-cart-bar price-text'), `${price} ₽`, {
      searchType: 'like',
    })
  }
}
