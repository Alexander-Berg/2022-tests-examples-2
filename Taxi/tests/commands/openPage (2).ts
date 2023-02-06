import {generateUUID, mkTestId, prepareDomStylesForTests} from '../utils'

const APP_HOST = `http://${process.env.DOCKER_HOST_INTERNAL}:${process.env.APP_CLIENT_PORT}`

export interface OpenPageOptions {
  cookies?: Record<string, string>
}

export async function openPage(this: WebdriverIO.Browser, pathname: string, options?: OpenPageOptions) {
  /* open empty page to set default cookies */
  await this.url(`${APP_HOST}/e2e/test-page`)
  await this.deleteAllCookies()

  const testUid = generateUUID()
  /* standId used on server for parallel tests execution (prevent database conflicts) */
  const cookies = [
    {name: 'standId', value: testUid},
    {name: 'testUid', value: testUid},
    {name: 'e2eAuthorizeOk', value: 'true'},
  ]

  if (options?.cookies) {
    Object.entries(options.cookies).map(([name, value]) => {
      cookies.push({name: name, value: value})
    })
  }

  await this.setCookies(cookies)

  await this.back()

  await this.url(`${APP_HOST}${pathname}`)
  await this.waitForElementExists(mkTestId('document-loaded'), {timeout: 20000})
  await this.execute(prepareDomStylesForTests)
}

export type OpenPage = typeof openPage
