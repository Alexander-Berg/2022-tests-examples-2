import {WaitForOptions} from 'webdriverio/build/types'

import {AssertImageOptions} from '../commands'
import {mkDataDisabled, mkDataLoading, mkTestId} from '../utils'

import {Browser} from './Browser'

export class BaseMobilePage extends Browser {
  private cartButtonId = mkTestId('cart-button')

  async waitForCartButtonActive(options?: {loading?: boolean; reverse?: boolean}) {
    await this.browser.waitForElementExists(`${this.cartButtonId}${mkDataLoading(options?.loading ? 'true' : 'false')}`)
    await this.browser.waitForElementExists(
      `${this.cartButtonId}${mkDataDisabled(options?.reverse ? 'true' : 'false')}`,
    )
  }

  async waitForCartButtonTextLike(text: string) {
    await this.browser.waitForElementText(`${this.cartButtonId} ${mkTestId('price-text')}`, text, {searchType: 'like'})
  }

  async waitForCartButtonExists(options?: WaitForOptions) {
    await this.browser.waitForElementExists(this.cartButtonId, options)
  }

  async waitAndClickCartButton() {
    await this.browser.waitForElementAndClick(this.cartButtonId)
  }

  async assertBodyImage(options?: AssertImageOptions) {
    await this.browser.assertImage('body', options)
  }

  async waitForSkeleton() {
    await this.browser.waitForElementExists(mkTestId('app-skeleton'))
  }
}
