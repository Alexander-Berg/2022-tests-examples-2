type Params =
  | {
      x: number
      y?: number
    }
  | {x?: number; y: number}

export async function scrollByElement(this: WebdriverIO.Browser, selector: string, params: Params) {
  const element = await this.$(selector)

  await this.execute(
    (element, params) => {
      if (element instanceof Element) {
        element.scrollBy(params.x ?? 0, params.y ?? 0)
      }
    },
    element,
    params,
  )
}

export type ScrollByElement = typeof scrollByElement
