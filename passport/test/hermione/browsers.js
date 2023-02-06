/**
 * В этом файле перечислен список браузеров, поддерживаемых в рамках проекта.
 *
 * Как добавить браузер:
 *   - добавить новый ключ с именем браузера в объект browsers
 *   - в качестве значения нужно добавить объект, содержащий следующие поля:
 *     - desiredCapabilities, если браузер автоматизирован в обоих инструментах и имеет общие capabilities
 *     - hermione с настройками для Hermione, если браузер автоматизирован в Hermione
 *
 * Все настройки для инструментов должны соответствовать требуемому инструментом формату.
 */

const _ = require('lodash');

const DISABLE_GEO = {
    profile: {
        default_content_setting_values: {
            geolocation: 2
        }
    }
};

const acceptInsecureCerts = [process.env.HOST_ENV, process.env.TEST_ENV].includes('dev');

const browsers = {
    'edge-desktop': {
        desiredCapabilities: {
            browserName: 'MicrosoftEdge',
            version: '17.1', // TODO: добавить более новую версию edge
            acceptInsecureCerts,
            acceptSslCerts: process.env.TEST_ENV === 'dev' // TODO: не помогает
        },
        hermione: {
            // // TODO: использовать квоту selenium / selenium, добавив туда нужные браузеры
            gridUrl: 'http://web4:c0545734536d4a8efa644f6c4d706c34@sg.yandex-team.ru:4444/wd/hub',
            // Edge рендерит картинки, которые только что попали во viewport, с некоторой задержкой
            // @see https://st.yandex-team.ru/SERP-77768
            screenshotDelay: 400,
            meta: {platform: 'desktop'},
            windowSize: '1280x1024',
            compositeImage: true,
            sessionEnvFlags: {isW3C: false}
        }
    },
    firefox46: {
        desiredCapabilities: {
            browserName: 'firefox',
            version: '46',
            acceptInsecureCerts
        }
    },
    firefox: {
        desiredCapabilities: {
            browserName: 'firefox',
            browserVersion: '89.0',
            acceptInsecureCerts
        },
        hermione: {
            testsPerSession: 5,
            calibrate: false,
            compositeImage: true,
            windowSize: '1280x972',
            meta: {platform: 'desktop'}
        }
    },
    'chrome-desktop': {
        desiredCapabilities: {
            browserName: 'chrome',
            browserVersion: '91.0',
            acceptInsecureCerts,
            'goog:chromeOptions': {
                prefs: _.merge(
                    {
                        credentials_enable_service: false,
                        profile: {
                            default_content_setting_values: {
                                password_manager_enabled: false
                            }
                        }
                    },
                    DISABLE_GEO
                )
            },
            'goog:loggingPrefs': {
                browser: 'ALL'
            }
        },
        hermione: {
            calibrate: false,
            compositeImage: true,
            meta: {platform: 'desktop'},
            windowSize: '1280x1024'
        }
    },
    'chrome-desktop-1920': {
        desiredCapabilities: {
            browserName: 'chrome',
            browserVersion: '91.0',
            acceptInsecureCerts,
            'goog:chromeOptions': {
                prefs: _.merge(
                    {
                        credentials_enable_service: false,
                        profile: {
                            default_content_setting_values: {
                                password_manager_enabled: false
                            }
                        }
                    },
                    DISABLE_GEO
                )
            }
        },
        hermione: {
            calibrate: false,
            compositeImage: true,
            meta: {platform: 'desktop'},
            windowSize: '1920x1080'
        }
    },
    ipad: {
        desiredCapabilities: {
            browserName: 'chrome',
            browserVersion: '91.0',
            acceptInsecureCerts,
            'goog:chromeOptions': {
                prefs: _.merge(
                    {
                        credentials_enable_service: false,
                        profile: {
                            default_content_setting_values: {
                                password_manager_enabled: false
                            }
                        }
                    },
                    DISABLE_GEO
                ),
                mobileEmulation: {
                    deviceMetrics: {
                        width: 1024,
                        height: 768,
                        pixelRatio: 2.0
                    },
                    userAgent: [
                        'Mozilla/5.0',
                        '(iPad; CPU OS 10_2_1 like Mac OS X)',
                        'AppleWebKit/602.4.6',
                        '(KHTML, like Gecko)',
                        'Version/10.0',
                        'Mobile/14D27',
                        'Safari/602.1'
                    ].join(' ')
                }
            }
        },
        hermione: {
            calibrate: true,
            compositeImage: true,
            screenshotMode: 'viewport',
            testsPerSession: 15,
            meta: {platform: 'desktop'}
        }
    },
    'ipad-portrait': {
        desiredCapabilities: {
            browserName: 'chrome',
            browserVersion: '91.0',
            acceptInsecureCerts,
            'goog:chromeOptions': {
                prefs: _.merge(
                    {
                        credentials_enable_service: false,
                        profile: {
                            default_content_setting_values: {
                                password_manager_enabled: false
                            }
                        }
                    },
                    DISABLE_GEO
                ),
                mobileEmulation: {
                    deviceMetrics: {
                        width: 768,
                        height: 1024,
                        pixelRatio: 2.0
                    },
                    userAgent: [
                        'Mozilla/5.0',
                        '(iPad; CPU OS 10_2_1 like Mac OS X)',
                        'AppleWebKit/602.4.6',
                        '(KHTML, like Gecko)',
                        'Version/10.0',
                        'Mobile/14D27',
                        'Safari/602.1'
                    ].join(' ')
                }
            }
        },
        hermione: {
            calibrate: true,
            compositeImage: true,
            screenshotMode: 'viewport',
            testsPerSession: 15,
            meta: {platform: 'desktop'}
        }
    },
    iphone: {
        desiredCapabilities: {
            browserName: 'chrome',
            browserVersion: '91.0',
            acceptInsecureCerts,
            'goog:chromeOptions': {
                prefs: _.merge(
                    {
                        credentials_enable_service: false,
                        profile: {
                            default_content_setting_values: {
                                password_manager_enabled: false
                            }
                        }
                    },
                    DISABLE_GEO
                ),
                mobileEmulation: {
                    deviceMetrics: {
                        width: 320,
                        height: 568,
                        pixelRatio: 2.0
                    },
                    userAgent: [
                        'Mozilla/5.0',
                        '(iPhone; CPU iPhone OS 10_1_1 like Mac OS X)',
                        'AppleWebKit/602.2.14',
                        '(KHTML, like Gecko)',
                        'Version/12.0',
                        'Mobile/14B100',
                        'Safari/602.1'
                    ].join(' ')
                }
            }
        },
        hermione: {
            calibrate: true,
            compositeImage: true,
            screenshotMode: 'viewport',
            screenshotDelay: 600,
            testsPerSession: 3,
            meta: {platform: 'touch-phone'}
        }
    },
    safari13: {
        desiredCapabilities: {
            version: '13.0',
            browserName: 'safari',
            isHeadless: false,
            acceptInsecureCerts
        },
        hermione: {
            gridUrl: 'http://ios:ios@sg.yandex-team.ru:4444/wd/hub',
            calibrate: false,
            compositeImage: true,
            resetCursor: false,
            testsPerSession: 50,
            screenshotDelay: 900,

            orientation: 'portrait',
            waitOrientationChange: false,
            sessionEnvFlags: {isW3C: false}, // TODO: FEI-22129
            meta: {platform: 'touch-phone'}
        }
    },
    iphoneX: {
        desiredCapabilities: {
            browserName: 'chrome',
            browserVersion: '91.0',
            acceptInsecureCerts,
            'goog:chromeOptions': {
                prefs: _.merge(
                    {
                        credentials_enable_service: false,
                        profile: {
                            default_content_setting_values: {
                                password_manager_enabled: false
                            }
                        }
                    },
                    DISABLE_GEO
                ),
                mobileEmulation: {
                    deviceName: 'iPhone X'
                }
            }
        },
        hermione: {
            calibrate: true,
            compositeImage: true,
            screenshotMode: 'viewport',
            screenshotDelay: 600,
            testsPerSession: 3,
            meta: {platform: 'touch-phone'}
        }
    },
    'chrome-phone': {
        desiredCapabilities: {
            browserName: 'chrome',
            browserVersion: '91.0',
            acceptInsecureCerts,
            'goog:chromeOptions': {
                prefs: DISABLE_GEO,
                mobileEmulation: {
                    deviceMetrics: {
                        width: 800,
                        height: 1280
                    },
                    userAgent: [
                        'Mozilla/5.0',
                        '(Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D)',
                        'AppleWebKit/535.19',
                        '(KHTML, like Gecko)',
                        'Chrome/18.0.1025.166',
                        'Mobile Safari/535.19'
                    ].join(' ')
                }
            }
        },
        hermione: {
            calibrate: true,
            compositeImage: true,
            screenshotMode: 'viewport',
            screenshotDelay: 600,
            testsPerSession: 3,
            meta: {platform: 'touch-phone'}
        }
    },
    'yandex-browser-phone': {
        desiredCapabilities: {
            browserName: 'chrome',
            browserVersion: '91.0',
            acceptInsecureCerts,
            'goog:chromeOptions': {
                mobileEmulation: {
                    userAgent: [
                        'Mozilla/5.0',
                        '(iPhone; CPU iPhone OS 12_2 like Mac OS X)',
                        'AppleWebKit/605.1.15',
                        '(KHTML, like Gecko)',
                        'Version/12.0',
                        'YaBrowser/19.4.2.561.10',
                        'Mobile/15E148',
                        'Safari/605.1'
                    ].join(' ')
                },
                prefs: {
                    credentials_enable_service: false,
                    profile: {
                        default_content_setting_values: {
                            password_manager_enabled: false
                        }
                    }
                }
            }
        },
        hermione: {
            calibrate: true,
            compositeImage: true,
            screenshotMode: 'viewport',
            screenshotDelay: 600,
            testsPerSession: 3,
            meta: {platform: 'touch-phone'}
        }
    }
};

/**
 * Возвращает конфигурацию браузеров
 * @returns {Object}
 */
function getBrowserConfigs() {
    const tool = 'hermione';

    return _(browsers)
        .pickBy(tool)
        .mapValues((browserConfig) => {
            const baseConfig = {desiredCapabilities: browserConfig.desiredCapabilities};

            return _.merge({}, baseConfig, browserConfig[tool]);
        })
        .value();
}

module.exports = {
    getBrowserConfigs
};
