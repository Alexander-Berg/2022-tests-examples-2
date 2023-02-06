const WAIT_FOR_CLICKABLE_TIMEOUT = 3000

export async function waitForElementAndClick(this: WebdriverIO.Browser, selector: string) {
  const element = await this.$(selector)

  await element.waitForClickable({
    timeout: WAIT_FOR_CLICKABLE_TIMEOUT,
    timeoutMsg: `Element for selector "${selector}" has not become clickable after ${WAIT_FOR_CLICKABLE_TIMEOUT}ms`,
  })

  await element.click()
}

export type WaitForElementAndClick = typeof waitForElementAndClick
