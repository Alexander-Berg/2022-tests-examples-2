import {
  createBaseConfig,
  createChromeSelenoidConfig,
  createBaseChromeDesiredCapabilities,
  HermioneConfig,
} from '@lavka/tests'

const windowSize = { width: 1680, height: 1050 }

const config: DeepPartial<HermioneConfig> = {
  ...createBaseConfig({ projectName: 'website' }),
  windowSize,
  sets: {
    website: {
      files: './sets/website',
    },
  },
  browsers: {
    chrome: {
      desiredCapabilities: {
        ...createBaseChromeDesiredCapabilities({
          windowSize,
        }),
        ...createChromeSelenoidConfig({
          name: 'lavka-website',
          windowSize,
        }),
      },
    },
  },
}

module.exports = config
