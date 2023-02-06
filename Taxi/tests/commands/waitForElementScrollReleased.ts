interface CheckScrollTickParams {
  prevScrollX: number | undefined
  prevScrollY: number | undefined
}

export async function waitForElementScrollReleased(this: WebdriverIO.Browser, selector: string) {
  const element = await this.$(selector)

  await this.execute(async element => {
    const NEXT_TICK_PAUSE_TIME = 100
    const TOTAL_PAUSE_TIME = 5000

    const checkElementScrollChangedTick = async (
      element: Element,
      params: CheckScrollTickParams,
      totalWaitTime = 0,
    ) => {
      const nextScrollX = element.scrollLeft
      const nextScrollY = element.scrollTop

      if (
        typeof params.prevScrollX !== 'undefined' &&
        typeof params.prevScrollY !== 'undefined' &&
        nextScrollY === params.prevScrollY &&
        nextScrollX === params.prevScrollX
      ) {
        return true
      }
      if (totalWaitTime > TOTAL_PAUSE_TIME) {
        // Если написать в несколько строчек, то отчёт hermione reporter съедает их.
        throw new Error(
          `Max checks that scroll has been stopped failed. Reason: Max attempts reached. Current element scroll: x ${nextScrollX} y ${nextScrollY}, prev x ${params.prevScrollX} prev y ${params.prevScrollY}`,
        )
      }

      await new Promise(resolve => setTimeout(resolve, NEXT_TICK_PAUSE_TIME))
      await checkElementScrollChangedTick(
        element,
        {prevScrollY: nextScrollY, prevScrollX: nextScrollX},
        totalWaitTime + NEXT_TICK_PAUSE_TIME,
      )
    }

    if (element instanceof Element) {
      await checkElementScrollChangedTick(element, {prevScrollX: undefined, prevScrollY: undefined})
    }
  }, element)
}

export type WaitForElementScrollReleased = typeof waitForElementScrollReleased
