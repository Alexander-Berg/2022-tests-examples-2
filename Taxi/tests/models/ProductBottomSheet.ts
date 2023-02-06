import {mkTestId, mkDataItemId} from '@lavka/tests'

import {BasePage} from './BasePage'
import {BundleBottomSheet} from './BundleBottomSheet'
import {Upsale} from './pieces'

const price = (value: number) => {
  return `${value} ₽`
}

export class ProductBottomSheet extends BasePage {
  async waitForExists() {
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
  }

  async assertImage(options?: {state: string}) {
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'), options)
  }

  async clickAddToCart() {
    await this.browser.waitForElementAndClick(mkTestId('add-to-cart-bar product-card-add-button'))
  }

  async clickAddSpin() {
    await this.browser.waitForElementAndClick(mkTestId('add-to-cart-bar add-spin-button'))
  }

  async clickRemoveSpin() {
    await this.browser.waitForElementAndClick(mkTestId('add-to-cart-bar remove-spin-button'))
  }

  async assertCartButtonPriceText(value: number) {
    // Ожидаем новое значение цены на кнопке, так как оно вернётся асинхронно позже
    await this.browser.waitForElementText(mkTestId('cart-button price-text'), price(value))
  }

  async assertCartButton(options?: {reverse: boolean}) {
    await this.browser.waitForElementExists(mkTestId('cart-button'), options)
  }

  async assertItemDetailsToast() {
    await this.browser.waitForElementDisplayed(mkTestId('item-details-toast'))
  }

  async clickItemDetailsToast() {
    await this.browser.waitForElementAndClick(mkTestId('item-details-toast'))
  }

  async waitForBodyScrollReleased() {
    await this.browser.waitForElementScrollReleased(mkTestId('bottom-sheet-body'))
  }

  getUpsale() {
    return new Upsale(this.ctx, 'product-card-bottom-sheet product-upsale')
  }

  async scrollToSection(section: string) {
    await this.browser.scrollToElement(`${mkTestId('product-card-bottom-sheet')} ${mkDataItemId(section)}`, {
      scrollableContainerSelector: mkTestId('bottom-sheet-body'),
      offsetY: -50,
    })
  }

  async scrollToBundleOptions() {
    await this.scrollToSection('bundle-options')
  }

  async scrollToBundleParts() {
    await this.scrollToSection('combo-parts')
  }

  async clickOnAvailableBundleItem(index: number) {
    await this.browser.waitForElementAndClick(mkTestId(`product-card-bottom-sheet available-bundles-item-${index}`))

    const bundleBottomSheet = new BundleBottomSheet(this.ctx)
    await bundleBottomSheet.waitForExists()

    return bundleBottomSheet
  }

  async clickTagsInformer() {
    await this.browser.waitForElementAndClick(
      `${mkTestId('product-card-bottom-sheet')} ${mkDataItemId('description')} ${mkTestId('informer')}`,
    )
  }
}
