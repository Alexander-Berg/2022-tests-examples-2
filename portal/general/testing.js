module.exports = {
  allYandexServicesUrl: 'https://l7test.yandex.{tld}/all',

  blackbox: {
    api: 'https://blackbox-mimino.yandex.net',
  },

  bunker: {
    api: 'http://bunker-api-dot.yandex.net/v1',
    version: 'latest',
  },

  mobileUrl: {
    ru: 'https://mobile.homepage.yandex.ru',
    ua: 'https://mobile.homepage.yandex.ua',
    kz: 'https://mobile.homepage.yandex.kz',
    by: 'https://mobile.homepage.yandex.by',
    'com.tr': 'https://mobile.homepage.yandex.com.tr',
  },

  softUrl: 'https://l7test.yandex.{tld}/soft',

  errorCounter: {
    env: 'testing',
  },
};
