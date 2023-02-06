import {WaitForOptions} from 'webdriverio/build/types'

const DEFAULT_WAIT_TIME = 10000

export async function waitForElementExists(this: WebdriverIO.Browser, selector: string, options?: WaitForOptions) {
  const element = await this.$(selector)
  await element.waitForExist({timeout: DEFAULT_WAIT_TIME, ...options})
}

export type WaitForElementExists = typeof waitForElementExists
