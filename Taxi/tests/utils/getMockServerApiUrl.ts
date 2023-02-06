export const getMockServerApiUrl = async (browser: WebdriverIO.Browser) => {
  return await browser.execute(() => `${window.serverData.apiBaseURL}/api-mock`)
}
