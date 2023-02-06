import type { OpenPageOptions } from '@lavka/tests'
import { mkTestId } from '@lavka/tests'

import { MobilePage } from './MobilePage'

export class CategoryPageMobile extends MobilePage {
  private layoutId = mkTestId('category-page-blocks')

  async openPage(categoryId: string, options?: OpenPageOptions) {
    await this.open(`/category/${categoryId}`, options)
    await this.waitForPageLoaded()
  }

  async waitForPageLoaded() {
    await this.browser.waitForElementExists(this.layoutId)
  }
}
