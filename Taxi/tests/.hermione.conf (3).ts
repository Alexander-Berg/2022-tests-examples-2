import {commonConfig} from './configs/commonConfig'
import {
  createBaseConfig,
  createChromeSelenoidConfig,
  createBaseChromeDesiredCapabilities,
  HermioneConfig,
} from '@lavka/tests'

const config: DeepPartial<HermioneConfig> = {
  ...createBaseConfig({projectName: 'webview'}),
  sets: {
    webview: {
      files: './sets/webview',
    },
  },
  browsers: {
    chrome: {
      desiredCapabilities: {
        ...createBaseChromeDesiredCapabilities({
          mobileEmulation: {
            deviceMetrics: {
              width: 375,
              height: 667,
              pixelRatio: 2.0,
            },
            userAgent: commonConfig.browser.userAgent.ios.lavkaApp,
          },
        }),
        ...createChromeSelenoidConfig({
          name: 'lavka-webview',
        }),
      },
    },
  },
}

module.exports = config
