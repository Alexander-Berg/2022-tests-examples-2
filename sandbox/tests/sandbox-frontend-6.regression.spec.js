require('mocha-generators').install();

const assert = require('../helpers/chai/assert');
const config = require('../config');

const pages = config.pages;
const generalBlocks = config.blocks.general;

/**
 * Хелпер для should contain тестов саджеста
 *
 * @param {Object} browser this.browser
 * @param {Object} expectations например {
 *      include: ['SANDBOX'],
 *      notInclude: ['TEST_TASK', 'evilj0e']
 * }
 * @returns false || assert error
 */
function* checkExpectationsOnSuggest(browser, expectations) {
    if (!browser || !expectations) {
        return false;
    }

    yield browser.setValue(generalBlocks.suggest.input, expectations.input);
    yield browser.click(generalBlocks.suggest.searchButton);
    yield browser.waitForVisible(generalBlocks.suggest.popup, config.options.pendingTime);
    yield browser.pause(200);

    const texts = yield browser.getText(generalBlocks.suggest.popup);

    assert.batch(texts, expectations.batch);
}

describe('sandbox-frontend-6: [Гость] Подсказывание пользователю значений в шапке сервиса поле ввода', () => {
    before(function* () {
        const browser = this.browser;

        yield browser.url(pages.root.url);
        yield browser.waitForVisible(generalBlocks.loader.main, config.options.pendingTime, true);
        yield browser.waitForExist(generalBlocks.suggest.input, config.options.pendingTime);
    });

    it('Должен показывать подсказку для поля ввода в шапке при вводе данных', function* () {
        const browser = this.browser;

        yield browser.setValue(generalBlocks.suggest.input, 'BUILD');
        yield browser.click(generalBlocks.suggest.searchButton);
        yield browser.waitForVisible(generalBlocks.suggest.popup, config.options.pendingTime);
    });

    it('Должен подсказывать блоки: Usergroups, Types, Resources и не подсказывать Users', function* () {
        const expectations = {
            input: 'ab',
            batch: {
                include: ['User groups', 'Task types', 'Resource type'],
                notInclude: ['Users']
            }
        };

        yield checkExpectationsOnSuggest(this.browser, expectations);
    });

    it('Должен подсказывать Usergroup по полному совпадению', function* () {
        const expectations = {
            input: 'AB-TESTING',
            batch: {
                include: ['User groups\u000AAB-TESTING', 'Task types', 'Resource type']
            }
        };

        yield checkExpectationsOnSuggest(this.browser, expectations);
    });

    it('Должен подсказывать Task type по полному совпадению', function* () {
        const expectations = {
            input: 'BUILD_SANDBOX_ARCHIVE',
            batch: {
                include: ['Task types\u000ABUILD_SANDBOX_ARCHIVE', 'Resource type'],
                notInclude: ['User groups']
            }
        };

        yield checkExpectationsOnSuggest(this.browser, expectations);
    });

    it('Должен подсказывать Resource type по полному совпадению', function* () {
        const expectations = {
            input: 'SANDBOX_ARCHIVE',
            batch: {
                include: ['Task types', 'Resource type\u000ASANDBOX_ARCHIVE'],
                notInclude: ['User groups']
            }
        };

        yield checkExpectationsOnSuggest(this.browser, expectations);
    });

    xit('Поле ввода должно очиститься при нажатии на кнопку очистки поля', function* () {
        const browser = this.browser;
        const expectations = { input: 'BUILD' };

        yield browser.setValue(generalBlocks.suggest.input, expectations.input);
        yield browser.click(generalBlocks.suggest.clearButton);

        const value = yield browser.getValue(generalBlocks.suggest.input);

        if (assert.isString(value)) {
            assert.equal(value, '');
        }
    });
});

describe('sandbox-frontend-6: ' +
         '[Авторизован] Подсказывание пользователю значений в шапке сервиса поле ввода', () => {
    before(function* () {
        const browser = this.browser;

        yield browser.url(pages.root.url);
        yield browser.setUser('user');
        yield browser.waitForVisible(generalBlocks.loader.main, config.options.pendingTime, true);
        yield browser.waitForExist(generalBlocks.suggest.input, config.options.pendingTime);
    });

    it('Должен показывать подсказку для поля ввода в шапке при вводе данных', function* () {
        const browser = this.browser;

        yield browser.setValue(generalBlocks.suggest.input, 'BUILD');
        yield browser.click(generalBlocks.suggest.searchButton);
        yield browser.waitForVisible(generalBlocks.suggest.popup, config.options.pendingTime);
    });

    it('Должен подсказывать блоки: Users, Usergroups, Types, Resources', function* () {
        const expectations = {
            input: 'ab',
            batch: {
                include: ['Users', 'User groups', 'Task types', 'Resource type']
            }
        };

        yield checkExpectationsOnSuggest(this.browser, expectations);
    });

    it('Должен подсказывать Users по полному совпадению', function* () {
        const expectations = {
            input: 'evilj0e',
            batch: {
                include: ['Users\u000Aevilj0e', 'Task types', 'Resource type']
            }
        };

        yield checkExpectationsOnSuggest(this.browser, expectations);
    });

    it('Должен подсказывать Usergroup по полному совпадению', function* () {
        const expectations = {
            input: 'AB-TESTING',
            batch: {
                include: ['User groups\u000AAB-TESTING', 'Task types', 'Resource type']
            }
        };

        yield checkExpectationsOnSuggest(this.browser, expectations);
    });

    it('Должен подсказывать Task type по полному совпадению', function* () {
        const expectations = {
            input: 'BUILD_SANDBOX_ARCHIVE',
            batch: {
                include: ['Task types\u000ABUILD_SANDBOX_ARCHIVE', 'Resource type'],
                notInclude: ['User groups']
            }
        };

        yield checkExpectationsOnSuggest(this.browser, expectations);
    });

    it('Должен подсказывать Resource type по полному совпадению', function* () {
        const expectations = {
            input: 'SANDBOX_ARCHIVE',
            batch: {
                include: ['Task types', 'Resource type\u000ASANDBOX_ARCHIVE'],
                notInclude: ['User groups']
            }
        };

        yield checkExpectationsOnSuggest(this.browser, expectations);
    });

    xit('Поле ввода должно очиститься при нажатии на кнопку очистки поля', function* () {
        const browser = this.browser;
        const expectations = { input: 'BUILD' };

        yield browser.setValue(generalBlocks.suggest.input, expectations.input);
        yield browser.click(generalBlocks.suggest.clearButton);

        const value = yield browser.getValue(generalBlocks.suggest.input);

        assert.equal(value, '');
    });
});
