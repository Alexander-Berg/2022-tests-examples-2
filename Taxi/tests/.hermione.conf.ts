import * as Commands from './commands'
import type Hermione from 'hermione'
import {commonConfig} from './configs/commonConfig'

const addCommands = (browser: WebdriverIO.Browser) => {
  Object.keys(Commands).forEach(commandName => {
    const commands = Commands as Record<string, Parameters<typeof browser.addCommand>[1]>
    browser.addCommand(commandName, commands[commandName])
  })
}

const testsPerSession = 15

const getHostEntries = () => {
  // we have own containers network on ci
  if (process.env.CI) {
    return []
  }
  if (process.platform === 'linux') {
    // work in QYP to communicate with localhost from docker
    return ['host.docker.internal:172.17.0.1']
  }
  // assume that current docker supports host definition
  return ['host.docker.internal:host-gateway']
}

const config: DeepPartial<Hermione.Config> = {
  gridUrl: `http://${process.env.SELENIUM_HOST ?? 'localhost'}:4444/wd/hub`,
  system: {
    workers: testsPerSession,
    fileExtensions: ['.js'],
    mochaOpts: {
      slow: 10000, // If test execution time is greater than this value, then the test is slow.
      timeout: 1000000, // this.browser.debug timeout
    },
  },
  sets: {
    // @ts-ignore
    webview: {
      files: './sets/webview',
    },
  },

  plugins: {
    'html-reporter/hermione': {
      defaultView: 'all',
      enabled: true,
      path: '.dev/reports/hermione-reports',
      saveErrorDetails: true,
      scaleImages: true,
    },
  },
  screenshotsDir: '../../images',
  screenshotDelay: 100,
  tolerance: 2.5,
  antialiasingTolerance: 8,
  screenshotMode: 'viewport',
  assertViewOpts: {allowViewportOverflow: true},
  waitTimeout: 5000,
  resetCursor: true,
  strictSSL: false,
  /* Слишком много sessionsPerBrowser === долго запускаются и стартуют тесты
   Слишком мало sessionsPerBrowser === долго прогоняются тесты, нужно найти золотую середину */
  sessionsPerBrowser: process.env.E2E_SESSIONS_PER_BROWSER ? Number(process.env.E2E_SESSIONS_PER_BROWSER) : 5,
  testsPerSession: testsPerSession,
  retry: process.env.E2E_TEST_RETRY ? Number(process.env.E2E_TEST_RETRY) : 0,
  testTimeout: process.env.E2E_TEST_TIMEOUT ? Number(process.env.E2E_TEST_TIMEOUT) : null,
  httpTimeout: process.env.CI ? 90000 : 30000,
  urlHttpTimeout: process.env.CI ? 90000 : 30000,
  headless: true,
  browsers: {
    chrome: {
      desiredCapabilities: {
        browserName: 'chrome',
        /*
          если запускать тесты локально без selenoid, то с этим параметром не выйдет, нужно удалить browserVersion
          https://st.yandex-team.ru/INFRADUTY-20344?from=bell#61c7832a5f9dc82649d94108
        */
        ...(process.env.USE_LOCALHOST !== 'true' && {browserVersion: '97.0'}),
        acceptInsecureCerts: true,
        'selenoid:options': {
          enableVNC: !process.env.CI,
          enableVideo: false,
          enableLog: false,
          applicationContainers: process.env.CI ? ['e2e_services'] : [],
          hostsEntries: getHostEntries(),
          /* Имя для отображения в selenoid-ui */
          name: 'lavka-webview',
        },
        // https://github.com/webdriverio/webdriverio/issues/476
        // @ts-ignore
        'goog:loggingPrefs': {
          browser: 'ALL',
        },
        'goog:chromeOptions': {
          args: [
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--accept-insecure-certificates',
            '--disable-gpu',
            '--no-sandbox',
          ],
          //  * Скрывает системный диалог вверху окна браузера о том что браузер управляется тестовым софтом
          excludeSwitches: ['enable-automation'],
          mobileEmulation: {
            deviceMetrics: {
              width: 375,
              height: 667,
              pixelRatio: 2.0,
            },
            userAgent: commonConfig.browser.userAgent.ios.lavkaApp,
          },
        },
      },
    },
  },
  async prepareBrowser(browser: WebdriverIO.Browser) {
    addCommands(browser)
  },
}

module.exports = config
