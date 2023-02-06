export async function takeScreenshot(
    url: string,
    selector: string,
    screenshotFileName: string,
) {
    await this.browser.url(url);
    await this.browser.waitForVisible(selector);
    await this.browser.assertView(screenshotFileName, selector);
}
