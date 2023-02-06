import type { OpenPageOptions } from '@lavka/tests'
import { mkTestId } from '@lavka/tests'

import { MobilePage } from './MobilePage'

interface OpenPageMobileOptions extends OpenPageOptions {
  /* ожидать ли заглушку */
  waitForStub?: boolean
}

export class CatalogPageMobile extends MobilePage {
  private layoutId = mkTestId('catalog-page-section-bottom')
  private stabFallbackId = mkTestId('mobile-fallback')

  async openPage(options?: OpenPageMobileOptions) {
    await this.open('/', options)
    if (options?.waitForStub) {
      await this.browser.waitForElementExists(this.stabFallbackId)
    } else {
      await this.waitForPageLoaded()
    }
  }

  async waitForPageLoaded() {
    await this.browser.waitForElementExists(this.layoutId)
  }
}
