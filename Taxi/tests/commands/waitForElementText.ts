import {WaitUntilOptions} from 'webdriverio/build/types'

const TIMEOUT = 5000

/* Подумать, может заменить на text like */
export async function waitForElementText(
  this: WebdriverIO.Browser,
  selector: string,
  text: string,
  options?: WaitUntilOptions,
) {
  const element = await this.$(selector)
  await element.waitUntil(
    async function () {
      return (await element.getText()) === text
    },
    {
      timeout: TIMEOUT,
      timeoutMsg: `expected text: ${text} to be different after ${TIMEOUT}ms`,
      ...options,
    },
  )
}

export type WaitElementForText = typeof waitForElementText
