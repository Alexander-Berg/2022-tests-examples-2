import {mkDataId, mkTestId, AssertImageOptions, mkDataItemId} from '@lavka/tests'

import {BasePage, OpenPageOptions} from './BasePage'

import {HEADER_SCROLL_COMPENSATION} from '../constants'

export class MainPage extends BasePage {
  async openPage(options?: OpenPageOptions & {skipWaitingForLayout?: boolean}) {
    await this.open('/', options)
    if (!options?.skipWaitingForLayout) {
      await this.waitForPageLoaded()
    }
  }

  async waitForPageLoaded() {
    await this.browser.waitForElementExists(mkTestId('main-page-layout'))
  }

  async waitForMarketPackageModal() {
    await this.waitForModal('market-package-promo-modal')
  }

  async assertImage(options?: AssertImageOptions) {
    await this.browser.assertImage(mkTestId('main-page-layout'), options)
  }

  async waitAndClickForCategoryCard(categoryId: string) {
    const selector = `${mkTestId('category-card')}${mkDataItemId(categoryId)}`
    await this.browser.waitForElementAndClick(selector)
  }

  async scrollToPromoInformer(informerId: string) {
    await this.browser.scrollToElement(`${mkTestId('promo-informer')}${mkDataId(informerId)}`, {
      offsetY: HEADER_SCROLL_COMPENSATION,
    })
  }

  async waitAndClickOnPromoInformer(informerId: string) {
    const informerSelector = `${mkTestId('promo-informer')}${mkDataId(informerId)}`
    await this.browser.waitForElementAndClick(informerSelector, {waitForNotActiveAfterClick: true})
  }
}
