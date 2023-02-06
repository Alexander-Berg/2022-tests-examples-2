export interface ScrollToElementOptions {
  offsetY?: number
  offsetX?: number
  scrollAxis?: 'horizontal' | 'vertical'
  scrollableContainerSelector?: string
}

/* scroll in one direction to element inside passed container */
/* it's more controlled than native "scrollIntoView" method */
export async function scrollToElement(this: WebdriverIO.Browser, selector: string, options?: ScrollToElementOptions) {
  const {offsetY = 0, offsetX = 0, scrollableContainerSelector = 'body', scrollAxis = 'vertical'} = options || {}

  const element = await this.$(selector)

  const {y: elementYOffset, x: elementXOffset} = await this.execute(element => {
    if (!(element instanceof HTMLElement)) {
      throw new Error('element is not HTMLElement')
    }
    const {y, x} = element.getBoundingClientRect()
    return {y, x}
  }, element)

  await this.scrollByElement(scrollableContainerSelector, {
    x: scrollAxis === 'horizontal' ? elementXOffset + offsetX : 0,
    y: scrollAxis === 'vertical' ? elementYOffset + offsetY : 0,
  })
}

export type ScrollToElement = typeof scrollToElement
