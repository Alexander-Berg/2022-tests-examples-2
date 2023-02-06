import {WaitForOptions} from 'webdriverio/build/types'

import {WAIT_FOR_ELEMENT_TIMEOUT} from '@lavka/constants'

export interface WaitForElementExistsOptions extends WaitForOptions {
  waitForNotActiveAfterClick?: boolean
}

export async function waitForElementExists(
  this: WebdriverIO.Browser,
  selector: string,
  options?: WaitForElementExistsOptions,
) {
  const element = await this.$(selector)

  if (options?.waitForNotActiveAfterClick) {
    const elementWithActive = await this.$(`${selector}:not(:active)`)
    await elementWithActive.waitForExist({timeout: WAIT_FOR_ELEMENT_TIMEOUT, ...options})
  }

  await element.waitForExist({timeout: WAIT_FOR_ELEMENT_TIMEOUT, ...options})
}

export type WaitForElementExists = typeof waitForElementExists
