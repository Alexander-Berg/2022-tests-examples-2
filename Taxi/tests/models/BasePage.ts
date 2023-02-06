import type { OpenPageOptions, AssertImageOptions } from '@lavka/tests'
import { Browser, mkDataItemId, mkDataLoading, mkTestId } from '@lavka/tests'

export class DesktopPage extends Browser {
  private catalogWrapperTestId = mkTestId('catalog-wrapper')

  async open(path: string, options?: OpenPageOptions) {
    await this.browser.openPage(path, { ...options, cookies: { ...options?.cookies, hideDevtools: 'true' } })
  }

  async assertCatalogWrapperImage(options?: AssertImageOptions) {
    await this.browser.assertImage(this.catalogWrapperTestId, options)
  }

  async waitAndClickBreadCrumbs(num: number) {
    await this.browser.waitForElementAndClick(`${mkTestId('breadcrumbs')} ${mkDataItemId(String(num))}`)
  }

  async waitForHeaderCartButtonLoaded() {
    await this.browser.waitForElementExists(`${mkTestId('cart-info')}${mkDataLoading('false')}`)
  }

  async waitForSideCartButtonLoaded() {
    await this.browser.waitForElementExists(mkTestId('cart-loading-button'), { reverse: true })
    await this.browser.waitForElementExists(mkTestId('order-button'))
  }
}
