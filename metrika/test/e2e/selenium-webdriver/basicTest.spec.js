const chai = require('chai');
const { By } = require('selenium-webdriver');
const e2eUtils = require('../utils/index.js');
const { TestCase } = require('./utils.js');

describe('base ie8 test', function () {
    const test = new TestCase({
        instance: this,
        browser: 'internet explorer',
        version: 8,
    });
    const counterId = 26302566;
    const testGoal = 'testGoal';
    const testParams = { a: { b: 2 } };
    const firstPageUrl = `${test.baseUrl}/firstPage.hbs`;
    const secondPageUrl = `${test.baseUrl}/secondPage.hbs`;
    let browser;
    before(async function () {
        browser = await test.getBrowser();
    });
    beforeEach(async function () {
        await browser.get(firstPageUrl);
        await browser.executeScript(`document.cookie = 'gdpr=0'`);
    });
    it('send referer', async function () {
        await browser.findElement(By.css('#next')).click();
        const result = await e2eUtils.provideServerHelpers(browser, {
            cb(serverHelpers, options) {
                serverHelpers.collectRequests(
                    1000,
                    null,
                    options.regexp.defaultRequestRegEx,
                );
                new Ya.Metrika2({
                    id: options.counterId,
                });
            },
            counterId,
        })();
        const requests = result.map(e2eUtils.getRequestParams);
        chai.expect(requests).to.be.lengthOf(1);
        const [pageView] = requests;
        chai.expect(pageView.params['page-url']).to.be.eq(secondPageUrl);
        chai.expect(pageView.params['page-ref']).to.be.eq(firstPageUrl);
    });
    it('send params', async function () {
        const result = await e2eUtils.provideServerHelpers(browser, {
            cb(serverHelpers, options) {
                serverHelpers.collectRequests(
                    1000,
                    null,
                    options.regexp.defaultRequestRegEx,
                );
                const instance = new Ya.Metrika2({
                    id: options.counterId,
                });
                instance.params(options.testParams);
            },
            counterId,
            testParams,
        })();
        const requests = result.map(e2eUtils.getRequestParams);
        chai.expect(requests).to.be.lengthOf(2);
        const [, paramsReqest] = requests;
        chai.expect(paramsReqest.siteInfo).to.be.deep.eq(testParams);
    });
    it('send goal', async function () {
        const result = await e2eUtils.provideServerHelpers(browser, {
            cb(serverHelpers, options) {
                serverHelpers.collectRequests(
                    1000,
                    null,
                    options.regexp.defaultRequestRegEx,
                );
                const instance = new Ya.Metrika2({
                    id: options.counterId,
                });
                instance.reachGoal(options.testGoal);
            },
            counterId,
            testGoal,
        })();
        const requests = result.map(e2eUtils.getRequestParams);
        chai.expect(requests).to.be.lengthOf(2);
        const [, goal] = requests;
        const info = goal.params['page-url'];
        const [protocol] = info.split(':');
        const [pathname] = info.split('/').slice(-1);
        chai.expect(protocol).to.be.eq('goal');
        chai.expect(pathname).to.be.eq(`${testGoal}`);
    });
    it('send hit', async function () {
        const result = await e2eUtils.provideServerHelpers(browser, {
            cb(serverHelpers, options) {
                serverHelpers.collectRequests(
                    1000,
                    null,
                    options.regexp.defaultRequestRegEx,
                );
                new Ya.Metrika2({
                    id: options.counterId,
                });
            },
            counterId,
        })();
        const requests = result.map(e2eUtils.getRequestParams);
        chai.expect(requests).to.be.lengthOf(1);
        const [pageView] = requests;
        chai.expect(pageView.params['page-url']).to.be.eq(firstPageUrl);
        const title = await browser.getTitle();
        chai.expect(title).to.be.eq('title page test');
        chai.expect(pageView.brInfo.t).to.be.eq(title);

        chai.expect(pageView.brInfo.pv).to.be.eq('1');
    });
});
