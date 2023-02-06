export type HermioneConfig = DeepPartial<
  Hermione.Config & {
    strictSSL: boolean
    headless: boolean
    plugins: {
      // https://github.com/gemini-testing/html-reporter
      'html-reporter/hermione': unknown
    }
    screenshotsDir: string
    sets: {
      webview?: Hermione.Config['sets']
      website?: Hermione.Config['sets']
    }
  }
>

export type ChromeOptions = RequiredByKeys<WebDriver.DesiredCapabilities, 'chromeOptions'>['chromeOptions']

export interface WindowSize {
  width: number
  height: number
}
