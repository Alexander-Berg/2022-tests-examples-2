export interface TypeIntoOptions {
  clearBefore?: boolean
  blurOnEnd?: boolean
  eraseCountSymbols?: number
}

export async function typeText(this: WebdriverIO.Browser, selector: string, text: string, options?: TypeIntoOptions) {
  const {clearBefore, blurOnEnd, eraseCountSymbols} = options || {}
  const input = await this.$(selector)

  if (eraseCountSymbols) {
    for (let i = 0; i <= eraseCountSymbols; i++) {
      await this.keys('Backspace')
    }
  }

  if (clearBefore) {
    await input.click()
    await this.keys(['Control', 'a'])
    await this.keys('Delete')
    await input.setValue(text)
  } else {
    await input.addValue(text)
  }

  if (blurOnEnd) {
    await this.executeScript('arguments[0].blur()', [input])
  }
}

export type TypeText = typeof typeText
