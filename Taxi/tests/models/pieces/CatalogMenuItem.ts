import type { TestDefinitionCallbackCtx } from 'hermione'

import type { AssertImageOptions } from '@lavka/tests'
import { Browser, mkDataItemId, mkTestId } from '@lavka/tests'

interface Props {
  itemId: string
}

export class CatalogMenuItemCollapse extends Browser {
  protected readonly rootId = mkTestId('catalog-menu-item-collapse')
  protected readonly itemId: string

  constructor(ctx: TestDefinitionCallbackCtx, props: Props) {
    super(ctx)
    this.itemId = mkDataItemId(props.itemId)
  }

  get selector() {
    return `${this.rootId}${this.itemId}`
  }

  async moveTo() {
    const element = this.browser.$(this.selector)
    await element.moveTo()
  }

  async waitAndClick() {
    await this.browser.waitForElementAndClick(this.selector)
  }

  async waitAndClickSubItem(subItemId: string) {
    await this.browser.waitForElementAndClick(`${this.selector} ${mkDataItemId(subItemId)}`)
  }

  async assertImage(options?: AssertImageOptions) {
    await this.browser.assertImage(this.selector, options)
  }
}
