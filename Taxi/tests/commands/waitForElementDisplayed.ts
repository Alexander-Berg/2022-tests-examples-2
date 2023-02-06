import {WaitForOptions} from 'webdriverio/build/types'

import {WAIT_FOR_ELEMENT_TIMEOUT} from '@lavka/constants'

export type WaitForElementDisplayedOptions = WaitForOptions

export async function waitForElementDisplayed(
  this: WebdriverIO.Browser,
  selector: string,
  options?: WaitForElementDisplayedOptions,
) {
  const element = await this.$(selector)
  await element.waitForDisplayed({timeout: WAIT_FOR_ELEMENT_TIMEOUT, ...options})
}

export type WaitForElementDisplayed = typeof waitForElementDisplayed
