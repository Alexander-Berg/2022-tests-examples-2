import {WaitUntilOptions} from 'webdriverio/build/types'

import {WAIT_FOR_ELEMENT_TIMEOUT} from '@lavka/constants'

type WaitForElementTextOptions = WaitUntilOptions & {
  searchType: 'equal' | 'like'
}

/* Подумать, может заменить на text like */
export async function waitForElementText(
  this: WebdriverIO.Browser,
  selector: string,
  text: string,
  options?: WaitForElementTextOptions,
) {
  const element = await this.$(selector)
  const searchType = options?.searchType ?? 'equal'

  await element.waitUntil(
    async function () {
      const elementText = await element.getText()
      if (searchType === 'like') {
        return elementText.includes(text)
      }
      return elementText === text
    },
    {
      timeout: WAIT_FOR_ELEMENT_TIMEOUT,
      timeoutMsg: `expected text: ${text} for search type "${searchType}" to be different after ${WAIT_FOR_ELEMENT_TIMEOUT}ms`,
      ...options,
    },
  )
}

export type WaitElementForText = typeof waitForElementText
