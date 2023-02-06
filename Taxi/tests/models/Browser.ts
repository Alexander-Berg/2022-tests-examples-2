import {TestDefinitionCallbackCtx} from 'hermione'

import {AssertImageOptions, ScrollToElementEdgeOptions} from '../commands'

export class Browser {
  protected ctx: TestDefinitionCallbackCtx

  constructor(ctx: TestDefinitionCallbackCtx) {
    this.ctx = ctx
  }

  get browser() {
    return this.ctx.browser
  }

  async back() {
    await this.browser.back()
  }

  async debug() {
    await this.browser.debug()
  }

  async setInnerWindowSize(width: number, height: number) {
    await this.browser.setInnerWindowSize(width, height)
  }

  async waitForPageScrollReleased() {
    await this.browser.waitForElementScrollReleased('body')
  }

  async scrollBodyToEdge(options: ScrollToElementEdgeOptions) {
    await this.browser.scrollToElementEdge('body', options)
  }

  async assertImage(options?: AssertImageOptions) {
    await this.browser.assertImage('body', options)
  }

  async assertUrlPathname(urlPart: string) {
    await this.browser.assertUrlPathname(urlPart)
  }
}
