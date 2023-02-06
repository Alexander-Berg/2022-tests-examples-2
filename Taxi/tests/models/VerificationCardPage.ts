import {AssertImageOptions, mkTestId} from '@lavka/tests'

import {BasePage} from './BasePage'

export class VerificationCardPage extends BasePage {
  private layoutId = mkTestId('verification-card-page')

  async waitForPageLoaded() {
    await this.browser.waitForElementExists(this.layoutId)
  }
  async assertImage(options?: AssertImageOptions) {
    await this.browser.assertImage(this.layoutId, options)
  }
}
