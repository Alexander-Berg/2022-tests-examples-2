import path from 'path'

import * as Commands from '../commands'
import {invariant, translitRusEng} from '../utils'
import {getRootDirPath} from '../utils/getRootDirPath'
import {getSafeArcadiaFileName} from '../utils/getSafeRepoFileName'

import {HermioneConfig} from './types'

const addCommands = (browser: WebdriverIO.Browser) => {
  Object.keys(Commands).forEach(commandName => {
    const commands = Commands as Record<string, Parameters<typeof browser.addCommand>[1]>
    browser.addCommand(commandName, commands[commandName])
  })
}

const testsPerSession = 15

export const createBaseConfig = ({projectName}: {projectName: string}): HermioneConfig => {
  const testsImagesDir = path.join(getRootDirPath(), 'projects', projectName, 'tests/images')

  return {
    gridUrl: `http://${process.env.SELENIUM_HOST ?? 'localhost'}:4444/wd/hub`,
    system: {
      workers: testsPerSession,
      fileExtensions: ['.js'],
      mochaOpts: {
        slow: 10000,
        timeout: 1000000, // this.browser.debug timeout
      },
    },
    plugins: {
      'html-reporter/hermione': {
        defaultView: 'all',
        enabled: true,
        path: 'report',
        saveErrorDetails: true,
        scaleImages: true,
      },
    },
    screenshotsDir: (test: Hermione.Test) => {
      invariant(test.file)
      return path.join(
        testsImagesDir,
        path.basename(test.file).replace('.js', ''),
        getSafeArcadiaFileName(translitRusEng(test.title, {lowerCase: true})),
      )
    },
    screenshotDelay: 100,
    tolerance: 2.5,
    antialiasingTolerance: 8,
    screenshotMode: 'viewport',
    assertViewOpts: {allowViewportOverflow: true},
    waitTimeout: 5000,
    resetCursor: true,
    strictSSL: false,
    // /* Слишком много sessionsPerBrowser === долго запускаются и стартуют тесты
    //  Слишком мало sessionsPerBrowser === долго прогоняются тесты, нужно найти золотую середину */
    sessionsPerBrowser: process.env.E2E_SESSIONS_PER_BROWSER ? Number(process.env.E2E_SESSIONS_PER_BROWSER) : 3,
    testsPerSession: testsPerSession,
    retry: process.env.E2E_TESTS_RETRY ? Number(process.env.E2E_TESTS_RETRY) : 0,
    testTimeout: process.env.E2E_TEST_TIMEOUT ? Number(process.env.E2E_TEST_TIMEOUT) : null,
    httpTimeout: 90000,
    urlHttpTimeout: 90000,
    headless: true,
    prepareBrowser(browser: WebdriverIO.Browser) {
      addCommands(browser)
    },
  } as HermioneConfig
}
