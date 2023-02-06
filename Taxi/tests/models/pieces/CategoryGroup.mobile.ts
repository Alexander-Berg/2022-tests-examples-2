import {TestDefinitionCallbackCtx} from 'hermione'

import {ScrollToElementEdgeOptions} from '../../commands'
import {MOBILE_HEADER_SCROLL_COMPENSATION} from '../../constants'
import {mkDataItemId, mkTestId} from '../../utils'
import {Browser} from '../Browser'

interface Props {
  groupId: string
}

/* Обрати внимание, этот класс используется для тестов webview и touch website */
export class CategoryGroupMobile extends Browser {
  protected readonly categoryGroupId = mkTestId('category-group')
  protected readonly groupId: string

  constructor(ctx: TestDefinitionCallbackCtx, props: Props) {
    super(ctx)
    this.groupId = mkDataItemId(props.groupId)
  }

  get selector() {
    return `${this.categoryGroupId}${this.groupId}`
  }

  async scrollToSelf() {
    await this.browser.scrollToElement(this.selector, {
      offsetY: MOBILE_HEADER_SCROLL_COMPENSATION,
    })
  }

  async waitAndClickGroupAllButton() {
    await this.browser.waitForElementAndClick(`${this.selector} ${mkTestId('all-button')}`)
  }

  async clickMoreButton() {
    await this.browser.waitForElementAndClick(`${this.selector} ${mkTestId('more-button')}`)
  }

  async waitAndClickCategoryCard(categoryId: string) {
    await this.browser.waitForElementAndClick(`${this.selector} ${mkDataItemId(categoryId)}`)
  }

  async waitAndClickProduct(productId: string) {
    await this.browser.waitForElementAndClick(`${this.selector} ${mkTestId(productId)}`)
  }

  async addProduct(productId: string) {
    await this.browser.waitForElementAndClick(
      `${this.selector} ${mkTestId(productId)} ${mkTestId('product-card-add-button')}`,
    )
  }
  async scrollToInformer() {
    await this.browser.scrollToElement(`${this.selector} ${mkTestId('informer')}`, {
      offsetY: MOBILE_HEADER_SCROLL_COMPENSATION,
    })
  }

  async waitAndClickOnInformer() {
    await this.browser.waitForElementAndClick(`${this.selector} ${mkTestId('informer')}`, {
      waitForNotActiveAfterClick: true,
    })
  }

  async scrollCarouselToEdge(options: ScrollToElementEdgeOptions) {
    await this.browser.scrollToElementEdge(`${this.selector} ${mkTestId('horizontal-scrollable-container')}`, options)
  }
}
