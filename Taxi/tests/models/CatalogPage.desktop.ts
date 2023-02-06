import type { OpenPageOptions } from '@lavka/tests'
import { mkTestId } from '@lavka/tests'

import { DesktopPage } from './DesktopPage'

export class CatalogPageDesktop extends DesktopPage {
  private layoutId = mkTestId('catalog-page-desktop')

  async openPage(options?: OpenPageOptions) {
    await this.open('/', options)
    await this.waitForPageLoaded()
  }

  async waitForPageLoaded() {
    await this.browser.waitForElementExists(this.layoutId)
  }
}
