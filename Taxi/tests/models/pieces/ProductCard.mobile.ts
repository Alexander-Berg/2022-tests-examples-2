import {TestDefinitionCallbackCtx} from 'hermione'

import {mkDataItemId, mkTestId} from '../../utils'
import {Browser} from '../Browser'

interface Props {
  productId: string
}

export class ProductCardMobile extends Browser {
  protected readonly rootId = mkTestId('product-card')
  protected readonly productId: string

  constructor(ctx: TestDefinitionCallbackCtx, props: Props) {
    super(ctx)
    this.productId = mkDataItemId(props.productId)
  }

  get selector() {
    return `${this.rootId}${this.productId}`
  }

  async addToCart(props?: {firstItem?: boolean}) {
    if (props?.firstItem) {
      await this.browser.waitForElementAndClick(`${this.selector} ${mkTestId('product-card-add-button')}`)
    }
  }

  async waitAndClick() {
    await this.browser.waitForElementAndClick(this.selector)
  }
}
