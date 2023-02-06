export interface ScrollIntoViewOptions extends ScrollOptions {
  vertical?: ScrollLogicalPosition
  horizontal?: ScrollLogicalPosition
}

export async function scrollIntoView(
  this: WebdriverIO.Browser,
  selector: string,
  options: ScrollIntoViewOptions = {vertical: 'start', horizontal: 'nearest'},
): Promise<void> {
  const element = await this.$(selector)
  await element.waitForExist()
  await element.scrollIntoView({
    behavior: options.behavior,
    block: options.vertical,
    inline: options.horizontal,
  })
}

export type ScrollIntoView = typeof scrollIntoView
