import {identifiers} from '@lavka/constants'
import type {AssertImageOptions, ScrollToElementEdgeOptions} from '@lavka/tests'
import {mkDataAnimationState, mkDataItemId, mkTestId} from '@lavka/tests'

import {BasePage, OpenPageOptions} from './BasePage'
import {ProductBottomSheet} from './ProductBottomSheet'

export class CategoryPage extends BasePage {
  private navigationBubblesId = mkTestId('navigation-bubbles')
  private navigationCarouselId = mkTestId('navigation-carousel')
  private navigationCarouselScrollableContainer = `${this.navigationCarouselId} ${mkTestId(
    'horizontal-scrollable-container',
  )}`
  private bubblePlateId = `${this.navigationCarouselId} ${mkTestId('bubble-plate')}`

  async openCategoryPage(params?: {categoryId?: string}, options?: OpenPageOptions) {
    await this.open(
      `/?group=${identifiers.groupBase}&category=${params?.categoryId ?? identifiers.categoryBase}`,
      options,
    )
    await this.waitForPageLoaded()
  }

  async openProduct(id: string) {
    await this.browser.waitForElementAndClick(
      [mkTestId('products-list-layout'), mkTestId(`product-id-${id}`)].join(' '),
    )

    const bottomSheet = new ProductBottomSheet(this)
    await bottomSheet.waitForExists()

    return bottomSheet
  }

  async waitForPageLoaded() {
    await this.browser.waitForElementExists(mkTestId('category-page-layout'))
  }

  async assertImage(options?: AssertImageOptions) {
    await this.browser.assertImage(mkTestId('category-page-layout'), options)
  }

  async waitAndClickOnNavigationBubble(bubbleId: string, options?: {skipWaitingAnimations: boolean}) {
    await this.browser.waitForElementAndClick(`${this.navigationBubblesId} ${mkDataItemId(bubbleId)}`)
    await this.browser.waitForElementScrollReleased('body')
    if (!options?.skipWaitingAnimations) {
      await this.waitForBubblePlateAnimationCompleted()
    }
  }

  async waitAndClickOnNavigationCarouselBubble(bubbleId: string, options?: {skipWaitingAnimations: boolean}) {
    await this.browser.waitForElementAndClick(`${this.navigationCarouselId} ${mkDataItemId(bubbleId)}`)
    await this.browser.waitForElementScrollReleased('body')
    if (!options?.skipWaitingAnimations) {
      await this.waitForBubblePlateAnimationCompleted()
    }
  }

  async waitForBubblePlateAnimationCompleted() {
    await this.browser.waitForElementExists(`${this.bubblePlateId}${mkDataAnimationState('completed')}`)
  }

  async waitForNavigationBubbles() {
    await this.browser.waitForElementExists(this.navigationBubblesId)
  }

  async waitAndClickOnNavigationBubbleMoreButton() {
    await this.browser.waitForElementAndClick(`${this.navigationBubblesId} ${mkDataItemId('more-button')}`)
    await this.browser.waitForElementExists(`${this.navigationBubblesId}${mkDataAnimationState('completed')}`)
  }

  async scrollToBubbleInBubbleNavigationContainer(bubbleId: string) {
    await this.browser.scrollToElement(`${this.navigationCarouselId} ${mkDataItemId(bubbleId)}`, {
      scrollableContainerSelector: this.navigationCarouselScrollableContainer,
      scrollAxis: 'horizontal',
    })
    await this.waitForBubblePlateAnimationCompleted()
  }

  async scrollNavigationCarouselToEdge(options: ScrollToElementEdgeOptions) {
    await this.browser.scrollToElementEdge(this.navigationCarouselScrollableContainer, options)
  }

  async addProductToCart(productId: string, options?: {firstProduct: boolean}) {
    const buttonSelector = !options?.firstProduct ? mkTestId('add-spin-button') : mkTestId('product-card-add-button')
    await this.browser.waitForElementAndClick(`${mkTestId(`product-id-${productId}`)} ${buttonSelector}`)
  }

  async removeProductFromCart(productId: string) {
    await this.browser.waitForElementAndClick(
      mkTestId(`products-list-layout product-id-${productId} remove-spin-button`),
    )
  }

  async waitForTagsBottomSheetExists() {
    await this.browser.waitForElementExists(mkTestId('tags-bottom-sheet'))
  }
}
