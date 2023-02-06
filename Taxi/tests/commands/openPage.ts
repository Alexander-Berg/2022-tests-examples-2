import {commonConfig} from '../configs/commonConfig'
import {generateUUID} from '../utils/generateUUID'
import {mkTestId} from '../utils/mkTestId'
import {prepareDomStylesForTests} from '../utils/prepareDomStylesForTests'

const BASE_URL = commonConfig.api.baseUrl
const BASE_URL_PATH = commonConfig.api.basePathname

interface Options {
  cookies?: Record<string, string>
}

export async function openPage(this: WebdriverIO.Browser, pathname: string, options?: Options) {
  /* open empty page to set default cookies */
  await this.url(`${BASE_URL}/e2e/test-page`)

  const testUid = generateUUID()
  /* standId used on server for parallel tests execution (prevent database conflicts) */
  await this.setCookies([{name: 'standId', value: testUid}])
  await this.setCookies([{name: 'testUid', value: testUid}])

  if (options?.cookies) {
    await Promise.all(
      Object.entries(options.cookies).map(([name, value]) => {
        return this.setCookies([{name: name, value: value}])
      }),
    )
  }

  await this.back()

  await this.url(`${BASE_URL}${BASE_URL_PATH}${pathname}`)
  await this.waitForElementExists(mkTestId('document-loaded'), {timeout: 20000})
  await this.execute(prepareDomStylesForTests)
}

export type OpenPage = typeof openPage
