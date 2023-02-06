import type { OpenPageOptions } from '@lavka/tests'
import { mkTestId } from '@lavka/tests'

import { DesktopPage } from './DesktopPage'

export class CategoryPageDesktop extends DesktopPage {
  private layoutId = mkTestId('category-page-desktop')

  async openPage(categoryId: string, options?: OpenPageOptions) {
    await this.open(`/category/${categoryId}`, options)
    await this.waitForPageLoaded()
  }

  async waitForPageLoaded() {
    await this.browser.waitForElementExists(this.layoutId)
  }
}
