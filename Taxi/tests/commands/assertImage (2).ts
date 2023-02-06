import {getSafeArcadiaFileName} from '../utils/getSafeRepoFileName'

export interface AssertImageOptions extends Hermione.AssertViewOpts {
  state?: string
  stretch?: boolean
}

const countMap = new Map<string, number>()

const getScreenshotStateText = (testUid: string, state?: string) => {
  const stateCount = countMap.get(testUid)
  const nextValue = !stateCount ? 1 : stateCount + 1
  countMap.set(testUid, nextValue)
  const nextNum = String(nextValue)
  if (state) {
    return `${nextNum}-${getSafeArcadiaFileName(state)}`
  }
  return nextNum
}

export async function assertImage(this: WebdriverIO.Browser, selector: string, options?: AssertImageOptions) {
  const {state: screenshotState, ...optionsRest} = options ?? {}
  const [testUid] = await this.getCookies('testUid')
  const state = getScreenshotStateText(testUid.value, screenshotState)

  if (options?.stretch) {
    const {outerHeight, pageHeight, outerWidth} = await this.execute(() => {
      return {pageHeight: document.body.scrollHeight, outerHeight: window.outerHeight, outerWidth: window.outerWidth}
    })
    await this.setWindowSize(outerWidth, pageHeight)
    await this.assertView(state, selector, optionsRest)
    await this.setWindowSize(outerWidth, outerHeight)
    return
  }

  await this.assertView(state, selector, optionsRest)
}

export type AssertImage = typeof assertImage
