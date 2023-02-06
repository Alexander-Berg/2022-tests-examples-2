const getDefaultHost = () => {
  return process.env.BROWSER_HOST ?? (process.env.USE_LOCALHOST !== 'true' ? 'host.docker.internal' : 'localhost')
}

export const commonConfig = {
  browser: {
    userAgent: {
      ios: {
        lavkaApp:
          'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) yandex-lavka/1.2.4.97477 YandexEatsKit/1.17.23 Lavka/Standalone',
      },
    },
  },
  api: {
    baseUrl: `http://${getDefaultHost()}:3300`,
    basePathname: '/4.0/grocery-superapp/lavka',
  },
}
