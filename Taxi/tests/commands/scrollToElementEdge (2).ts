type Direction = 'down' | 'left' | 'right' | 'up'

export type ScrollToElementEdgeOptions = {
  direction?: Direction
}

interface ScrollTickParams {
  prevScrollY: number | undefined
  prevScrollX: number | undefined
}

export async function scrollToElementEdge(
  this: WebdriverIO.Browser,
  selector: string,
  options?: ScrollToElementEdgeOptions,
) {
  const element = await this.$(selector)

  this.execute(
    async (element, direction) => {
      const SCROLL_STEP = 1000
      // Will scroll for SCROLL_STEP every PAUSE_TICK ms
      const PAUSE_TICK = 100
      const MAX_PAUSE_AMOUNT_TIME = 5000
      const STABLE_ITERATIONS_COUNT = 3

      const scrollTick = async (
        element: Element,
        {prevScrollY, prevScrollX}: ScrollTickParams,
        totalPause = 0,
        stableIterationsCount = 0,
      ) => {
        const currentScrollX = element.scrollLeft
        const currentScrollY = element.scrollTop
        let isStableIteration = false

        if (totalPause > MAX_PAUSE_AMOUNT_TIME) {
          // Если написать в несколько строчек, то отчёт hermione reporter съедает их.
          throw new Error(
            `Max checks that scroll has reached the edge. Reason: Max attempts reached. Current element scroll: x ${currentScrollX} y ${currentScrollY}, prev x ${prevScrollX} prev y ${prevScrollY}`,
          )
        }

        if (
          prevScrollY !== undefined &&
          prevScrollX !== undefined &&
          currentScrollX === prevScrollX &&
          currentScrollY === prevScrollY
        ) {
          if (stableIterationsCount === STABLE_ITERATIONS_COUNT) {
            return true
          }
          isStableIteration = true
        }

        switch (direction) {
          case 'down': {
            element.scrollBy(0, SCROLL_STEP)
            break
          }
          case 'up': {
            element.scrollBy(0, -SCROLL_STEP)
            break
          }
          case 'right': {
            element.scrollBy(SCROLL_STEP, 0)
            break
          }
          case 'left': {
            element.scrollBy(-SCROLL_STEP, 0)
            break
          }
        }

        await new Promise(resolve => setTimeout(resolve, PAUSE_TICK))
        await scrollTick(
          element,
          {prevScrollX: currentScrollX, prevScrollY: currentScrollY},
          totalPause + PAUSE_TICK,
          isStableIteration ? stableIterationsCount + 1 : 0,
        )
      }

      if (element instanceof Element) {
        await scrollTick(element, {prevScrollY: undefined, prevScrollX: undefined})
      }
    },
    element,
    options?.direction ?? 'down',
  )
}

export type ScrollToElementEdge = typeof scrollToElementEdge
