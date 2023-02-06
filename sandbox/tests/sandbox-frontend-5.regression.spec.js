require('mocha-generators').install();

const assert = require('../helpers/chai/assert');
const config = require('../config');

const pages = config.pages;
const generalBlocks = config.blocks.general;

describe('sandbox-frontend-5: [Гость] Логотип и лейбл в шапке сайта кликабельны', () => {
    before(function* () {
        const browser = this.browser;

        yield browser.url(pages.tasks.url);
        yield browser.waitForVisible(generalBlocks.service.logo, config.options.pendingTime);
    });

    it('Логотип Yandex должен перекинуть нас на /tasks', function* () {
        const browser = this.browser;

        yield browser.click(generalBlocks.service.logo);

        const url = yield browser.getRelativeUrl();

        assert.equal(url, pages.tasks.url);
    });

    it('Логотип Sandbox должен перекинуть нас на /tasks', function* () {
        const browser = this.browser;

        yield browser.click(generalBlocks.service.label);

        const url = yield browser.getRelativeUrl();

        assert.include(url, pages.tasks.url);
    });
});

describe('sandbox-frontend-5: [Авторизован] Логотип и лейбл в шапке сайта кликабельны', () => {
    before(function* () {
        const browser = this.browser;

        yield browser.url(pages.tasks.url);
        yield browser.setUser('user');
        yield browser.waitForVisible(generalBlocks.service.logo, config.options.pendingTime);
    });

    it('Логотип Yandex должен перекинуть нас на /tasks', function* () {
        const browser = this.browser;

        yield browser.click(generalBlocks.service.logo);

        const url = yield browser.getRelativeUrl();

        assert.equal(url, pages.tasks.url);
    });

    it('Логотип Sandbox должен перекинуть нас на /tasks', function* () {
        const browser = this.browser;

        yield browser.click(generalBlocks.service.label);

        const url = yield browser.getRelativeUrl();

        assert.include(url, pages.tasks.url);
    });
});
