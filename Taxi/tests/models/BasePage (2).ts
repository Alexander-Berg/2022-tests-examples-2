import {mkTestId, ScrollToElementEdgeOptions, BaseMobilePage} from '@lavka/tests'

export interface OpenPageOptions {
  cookies?: Record<string, string>
}

interface WaitForAppLoader {
  reverse?: boolean
}

const BASE_URL_PATH = '/4.0/grocery-superapp/lavka'

export class BasePage extends BaseMobilePage {
  async open(path: string, options?: OpenPageOptions) {
    await this.browser.openPage(`${BASE_URL_PATH}${path}`, options)
  }

  async waitForModal(modalId: string) {
    await this.browser.waitForElementExists(mkTestId(`modal ${modalId}`))
  }

  async waitAndClickForModalCancelButton(modalId: string) {
    await this.browser.waitForElementAndClick(mkTestId(`modal ${modalId} cancel-button`))
  }

  async waitAndClickForModalConfirmButton(modalId: string) {
    await this.browser.waitForElementAndClick(`${mkTestId('modal')} ${mkTestId(modalId)} ${mkTestId('confirm-button')}`)
  }

  async wait(ms: number) {
    await new Promise<void>(resolve => setTimeout(resolve, ms))
  }

  async getWindowInnerHeight() {
    return this.browser.execute(() => window.innerHeight)
  }

  /* click on top window coordinate where bottom sheet backdrop is always clickable */
  async waitAndClickBottomSheetBackdrop() {
    await this.browser.waitForElementAndClick('body', {
      y: -Math.floor((await this.getWindowInnerHeight()) / 2),
    })
  }

  async waitForAppLoader(options?: WaitForAppLoader) {
    const element = await this.browser.$('html')
    await element.waitUntil(
      async () => {
        const value = await element.getAttribute('data-global-loader')
        return options?.reverse ? value === null : value !== null
      },
      {timeout: 10000},
    )
  }

  async clickInformerModalActionUnsetButton() {
    await this.browser.waitForElementAndClick(
      `${mkTestId('informer-modal')} ${mkTestId('action-button')}[data-action-id="unset"]`,
    )
    await this.browser.waitForElementExists(mkTestId('informer-modal'), {reverse: true})
  }

  async clickInformerModalActionLinkButton() {
    await this.browser.waitForElementAndClick(
      `${mkTestId('informer-modal')} ${mkTestId('action-button')}[data-action-id="link"]`,
    )
  }

  async scrollBodyTo(position: number) {
    await this.browser.scrollByElement('body', {y: position})
  }

  async scrollBodyToEdge(options: ScrollToElementEdgeOptions) {
    await this.browser.scrollToElementEdge('body', options)
  }

  async waitForPageScrollReleased() {
    await this.browser.waitForElementScrollReleased('body')
  }

  async waitAndClickBackNavigationButton() {
    await this.browser.waitForElementAndClick(mkTestId('back-button'))
  }
}
