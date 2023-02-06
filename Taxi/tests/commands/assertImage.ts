/* Safe for arcadia https://docs.yandex-team.ru/devtools/src/arcadia#filestructure */
const allowedFileNameRegExp = /^[\.\{\}\-,\(\)\[\]\{\}\+=#\$@\!a-zA-Z0-9\s]*$/

const getSafeFileName = (name: string) => {
  if (!allowedFileNameRegExp.test(name)) {
    throw new Error(
      `Недопустимое имя файла для screenshot state: ${name}
       https://docs.yandex-team.ru/devtools/src/arcadia#filestructure`,
    )
  }
  return name.trim().replace(/\s/g, '_')
}

interface Options extends Hermione.AssertViewOpts {
  state?: string
}

const countMap = new Map<string, number>()

const getScreenshotStateText = (testUid: string, state?: string) => {
  if (state) {
    return getSafeFileName(state)
  }
  const stateCount = countMap.get(testUid)
  const nextValue = !stateCount ? 1 : stateCount + 1
  countMap.set(testUid, nextValue)
  return String(nextValue)
}

export async function assertImage(this: WebdriverIO.Browser, selector: string, options?: Options) {
  const {state: screenshotState, ...optionsRest} = options ?? {}
  const [testUid] = await this.getCookies('testUid')
  const state = getScreenshotStateText(testUid.value, screenshotState)

  await this.assertView(state, selector, optionsRest)
}

export type AssertImage = typeof assertImage
