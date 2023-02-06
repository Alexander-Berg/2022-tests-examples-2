import {ChromeOptions, WindowSize} from './types'

type ConfigProps = {
  mobileEmulation?: ChromeOptions['mobileEmulation']
  windowSize?: WindowSize
}

export type ChromeDesiredCapabilities = WebDriver.DesiredCapabilities & {
  'goog:loggingPrefs': {
    browser: 'ALL'
  }
}

export const createBaseChromeDesiredCapabilities = ({
  mobileEmulation,
  windowSize,
}: ConfigProps): ChromeDesiredCapabilities => ({
  browserName: 'chrome',
  /*
      если запускать тесты локально без selenoid, то с этим параметром не выйдет, нужно удалить browserVersion
      https://st.yandex-team.ru/INFRADUTY-20344?from=bell#61c7832a5f9dc82649d94108
    */
  ...(!process.env.E2E_SKIP_BROWSER_VERSION ? {browserVersion: '97.0'} : undefined),

  acceptInsecureCerts: true,
  // https://github.com/webdriverio/webdriverio/issues/476
  'goog:loggingPrefs': {
    browser: 'ALL',
  },
  'goog:chromeOptions': {
    args: [
      '--disable-setuid-sandbox',
      //  TODO: не открываются yamaps из за этой опции (нужна ли она?)
      // '--disable-web-security',
      '--accept-insecure-certificates',
      '--disable-gpu',
      '--no-sandbox',
      windowSize ? `--window-size=${windowSize.width}x${windowSize.height}x24` : undefined,
    ].filter(Boolean) as string[],
    //  * Скрывает системный диалог вверху окна браузера о том что браузер управляется тестовым софтом
    ...(mobileEmulation ? {mobileEmulation} : undefined),
    excludeSwitches: ['enable-automation'],
  },
})
