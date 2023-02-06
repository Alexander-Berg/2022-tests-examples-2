require('mocha-generators').install();

const config = require('../config');

const pages = config.pages;
const tasksBlocks = config.blocks.tasks;

describe('sandbox-frontend-4: [Гость] Отображение списка задач на странице tasks', () => {
    it('Должен отображаться выдача со списком задач на странице /tasks', function* () {
        const browser = this.browser;

        yield browser.url(pages.tasks.url);
        yield browser.waitForExist(tasksBlocks.results.item, config.options.pendingTime);
    });
});

describe('sandbox-frontend-4: [Авторизован] Отображение списка задач на странице tasks', () => {
    before(function* () {
        const browser = this.browser;

        yield browser.url(pages.tasks.url);
        yield browser.setUser('user');
    });

    it('Должен отображаться выдача со списком задач на странице /tasks', function* () {
        const browser = this.browser;

        yield browser.waitForExist(tasksBlocks.results.item, config.options.pendingTime);
    });
});
