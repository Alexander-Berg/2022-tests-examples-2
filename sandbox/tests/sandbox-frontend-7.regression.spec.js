require('mocha-generators').install();

const assert = require('../helpers/chai/assert');
const config = require('../config');

const pages = config.pages;
const generalBlocks = config.blocks.general;
const taskBlocks = config.blocks.tasks;
const resourceBlocks = config.blocks.resources;

/**
 * Хелпер для click тестов саджеста
 *
 * @param {Object} browser this.browser
 * @param {Object} expectations например {
 *           suggestItemValue: 'AB-TESTING',
 *           suggestItemType: 'owner',
 *           filterInput: taskBlocks.filter.owner
 *       };
 * @returns false || assert error
 */
function* checkSuggestClick(browser, expectations) {
    /* eslint max-statements: [1, 11] */

    const suggestItem = generalBlocks.suggest.suggestItem.replace('%', expectations.suggestItemValue);

    yield browser.setValue(generalBlocks.suggest.input, expectations.suggestItemValue);
    yield browser.click(generalBlocks.suggest.searchButton);
    yield browser.waitForVisible(generalBlocks.suggest.popup, config.options.pendingTime);
    yield browser.pause(250);
    yield browser.click(suggestItem);

    const url = yield browser.getUrl();

    assert.include(url, `${expectations.suggestItemType}=${expectations.suggestItemValue}`);

    yield browser.waitForVisible(expectations.filterInput, config.options.pendingTime);

    const ownerValue = yield browser.getValue(expectations.filterInput);

    assert.equal(ownerValue, expectations.suggestItemValue);
}

describe('sandbox-frontend-7: [Гость] Переход по подсказкам к полю ввода в шапке сервиса', () => {
    before(function* () {
        const browser = this.browser;

        yield browser.url(pages.root.url);
        yield browser.waitForVisible(generalBlocks.loader.main, config.options.pendingTime, true);
        yield browser.waitForExist(generalBlocks.suggest.input, config.options.pendingTime);
    });

    it('Должен отфильтровать задачи по owner=User groups', function* () {
        const expectations = {
            suggestItemValue: 'AB-TESTING',
            suggestItemType: 'owner',
            filterInput: taskBlocks.filter.owner
        };

        yield checkSuggestClick(this.browser, expectations);
    });

    it('Должен отфильтровать задачи по type=Task type', function* () {
        const expectations = {
            suggestItemValue: 'BUILD_SANDBOX_ARCHIVE',
            suggestItemType: 'type',
            filterInput: taskBlocks.filter.type
        };

        yield checkSuggestClick(this.browser, expectations);
    });

    it('Должен отфильтровать задачи по type=Resource type', function* () {
        const expectations = {
            suggestItemValue: 'SANDBOX_ARCHIVE',
            suggestItemType: 'type',
            filterInput: resourceBlocks.filter.type
        };

        yield checkSuggestClick(this.browser, expectations);
    });
});

describe('sandbox-frontend-7: [Авторизован] Переход по подсказкам к полю ввода в шапке сервиса', () => {
    before(function* () {
        const browser = this.browser;

        yield browser.url(pages.root.url);
        yield browser.setUser('user');
        yield browser.waitForVisible(generalBlocks.loader.main, config.options.pendingTime, true);
        yield browser.waitForExist(generalBlocks.suggest.input, config.options.pendingTime);
    });

    it('Должен отфильтровать задачи по owner=User', function* () {
        const expectations = {
            suggestItemValue: 'evilj0e',
            suggestItemType: 'owner',
            filterInput: taskBlocks.filter.owner
        };

        yield checkSuggestClick(this.browser, expectations);
    });

    it('Должен отфильтровать задачи по owner=User groups', function* () {
        const expectations = {
            suggestItemValue: 'AB-TESTING',
            suggestItemType: 'owner',
            filterInput: taskBlocks.filter.owner
        };

        yield checkSuggestClick(this.browser, expectations);
    });

    it('Должен отфильтровать задачи по type=Task type', function* () {
        const expectations = {
            suggestItemValue: 'BUILD_SANDBOX_ARCHIVE',
            suggestItemType: 'type',
            filterInput: taskBlocks.filter.type
        };

        yield checkSuggestClick(this.browser, expectations);
    });

    it('Должен отфильтровать задачи по type=Resource type', function* () {
        const expectations = {
            suggestItemValue: 'SANDBOX_ARCHIVE',
            suggestItemType: 'type',
            filterInput: resourceBlocks.filter.type
        };

        yield checkSuggestClick(this.browser, expectations);
    });
});
