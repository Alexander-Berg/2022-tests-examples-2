import {ScrollIntoViewOptions} from './scrollIntoView'

interface ScrollToElementOptions extends ScrollIntoViewOptions {
  offsetY?: number
}

export async function scrollToElement(this: WebdriverIO.Browser, selector: string, options?: ScrollToElementOptions) {
  const {offsetY, ...scrollOptions} = options || {}

  await this.scrollIntoView(selector, scrollOptions)

  if (offsetY) {
    await this.execute(
      function ({offsetY}) {
        document.body.scrollTop = document.body.scrollTop + offsetY
      },
      {offsetY},
    )
  }
}

export type ScrollToElement = typeof scrollToElement
