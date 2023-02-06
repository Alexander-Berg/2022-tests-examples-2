import {ClickOptions} from 'webdriverio/build/types'

import {WAIT_FOR_ELEMENT_TIMEOUT} from '@lavka/constants'

export interface WaitForElementAndClickOptions extends ClickOptions {
  waitForNotActiveAfterClick?: boolean
}

export async function waitForElementAndClick(
  this: WebdriverIO.Browser,
  selector: string,
  options?: WaitForElementAndClickOptions,
) {
  const element = await this.$(`${selector}`)

  await element.waitForClickable({
    timeout: WAIT_FOR_ELEMENT_TIMEOUT,
    timeoutMsg: `Element for selector "${selector}" has not become clickable after ${WAIT_FOR_ELEMENT_TIMEOUT}ms`,
  })

  await element.click(options)
  if (options?.waitForNotActiveAfterClick) {
    await this.waitForElementExists(`${selector}:not(:active)`)
  }
}

export type WaitForElementAndClick = typeof waitForElementAndClick
