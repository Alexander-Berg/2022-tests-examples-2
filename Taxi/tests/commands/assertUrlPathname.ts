import {expect} from 'chai'

export async function assertUrlPathname(this: WebdriverIO.Browser, urlPart: string) {
  const url = new URL(await this.getUrl())
  expect(url.pathname).to.be.includes(urlPart)
}

export type AssertUrlPathname = typeof assertUrlPathname
