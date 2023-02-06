export async function addStyles(this: WebdriverIO.Browser, styles: string): Promise<() => Promise<void>> {
  const styleElement = await this.execute(function (styles): HTMLStyleElement {
    const styleElement = window.document.createElement('style')
    styleElement.innerHTML = styles
    window.document.head.appendChild(styleElement)
    return styleElement
  }, styles)

  return async () => {
    await this.execute(function (styleElement): void {
      window.document.head.removeChild(styleElement)
    }, styleElement)
  }
}

export type AddStyles = typeof addStyles
