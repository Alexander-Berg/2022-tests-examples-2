export async function setInnerWindowSize(this: WebdriverIO.Browser, width: number, height: number) {
  await this.setWindowSize(width, height)
  const {innerWidth, innerHeight} = await this.execute(() => {
    return {innerWidth: window.innerWidth, innerHeight: window.innerHeight}
  })
  await this.setWindowSize(2 * width - innerWidth, 2 * height - innerHeight)
}

export type SetInnerWindowSize = typeof setInnerWindowSize
