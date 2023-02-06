const webdriver = require('selenium-webdriver');
const addContext = require('mochawesome/addContext');
const config = require('./config');

webdriver.promise.USE_PROMISE_MANAGER = false;

class TestCase {
    constructor(opt) {
        opt.instance.timeout(150000);
        opt.instance.retries(config.retries);
        this.instance = opt.instance;
        this.browserPromise = this.getDriver(opt.browser, opt.version);
        const self = this;
        // eslint-disable-next-line no-undef
        afterEach(async function () {
            if (!self.browser) {
                return;
            }
            if (this.currentTest.state === 'failed') {
                await self.screenShot(this);
            }
        });
        // eslint-disable-next-line no-undef
        after(async function () {
            if (self.browser) {
                await self.browser.quit();
            }
        });
    }

    baseUrl = `http://${config.asyncConfig.inHostname}:${config.asyncConfig.port}/test/selenium-webdriver`;

    hostName = config.asyncConfig.inHostname;

    async getBrowser() {
        this.browser = await this.browserPromise;
        return this.browser;
    }

    async getDriver(browser, version) {
        const result = await new webdriver.Builder()
            .usingServer(config.gridUrl)
            .forBrowser(browser, `${version}`)
            .build();
        result.manage().timeouts().setScriptTimeout(5000);
        result.executeAsync = result.executeAsyncScript;
        this.browser = result;
        return result;
    }

    async screenShot() {
        if (!this.browser) {
            return;
        }
        const base64Image = await this.browser.takeScreenshot();
        addContext(this.instance, {
            title: 'Page screenshot',
            value: `data:image/png;base64,${base64Image}`,
        });
    }
}

module.exports = {
    TestCase,
};
