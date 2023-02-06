require('mocha-generators').install();

const assert = require('../helpers/chai/assert');
const config = require('../config');

const pages = config.pages;

describe('sandbox-frontend-3: [Гость] Перенаправение на страницу задач, если пользователь пришёл на /', () => {
    it('Должен перенаправить со / на /tasks', function* () {
        const browser = this.browser;

        yield browser.url(pages.root.url);

        const url = yield browser.getRelativeUrl();

        assert.equal(url, pages.tasks.url);

        const title = yield browser.getTitle();

        assert.equal(title, pages.tasks.title);
    });
});

describe('sandbox-frontend-3: ' +
         '[Авторизован] Перенаправение на страницу задач, если пользователь пришёл на /', () => {
    before(function* () {
        const browser = this.browser;

        yield browser.url(pages.root.url);
        yield browser.setUser('user');
    });

    it('Должен перенаправить со / на /tasks', function* () {
        const browser = this.browser;

        yield browser.url(pages.root.url);

        const url = yield browser.getRelativeUrl();

        assert.equal(url, pages.tasks.url);

        const title = yield browser.getTitle();

        assert.equal(title, pages.tasks.title);
    });
});
