import type { OpenPageOptions } from '@lavka/tests'
import { mkTestId } from '@lavka/tests'

import { DesktopPage } from './DesktopPage'

export class GoodPageDesktop extends DesktopPage {
  private rootId = mkTestId('good-page-desktop')

  async openPage(
    { productId, categoryId, waitForLoaded = true }: { productId: string; categoryId: string; waitForLoaded?: boolean },
    options?: OpenPageOptions,
  ) {
    await this.open(`/category/${categoryId}/anySubcategoryId/goods/${productId}`, options)
    if (waitForLoaded) {
      await this.waitForPageLoaded()
    }
  }

  async waitForPageLoaded() {
    await this.browser.waitForElementExists(this.rootId)
  }

  async addToCart(options?: { firstItem?: boolean }) {
    if (options?.firstItem) {
      await this.browser.waitForElementAndClick(mkTestId('product-card-add-button'))
    } else {
      await this.browser.waitForElementAndClick(mkTestId('add-spin-button'))
    }
  }

  async removeFromCart() {
    await this.browser.waitForElementAndClick(mkTestId('remove-spin-button'))
  }

  async waitForUnavailablePlaceholder() {
    await this.browser.waitForElementExists(mkTestId('placeholder-unavailable'))
  }
}
