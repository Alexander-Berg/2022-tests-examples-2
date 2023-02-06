'use strict';

async function open() {
    await this.browser.$('.mini-suggest__input').then(elem => elem.click());
    await this.browser.$('.body_search_yes').then(elem => elem.waitForDisplayed());
}

async function close() {
    await this.browser.$('(//*[contains(@class, "mini-suggest__overlay")]' +
    '|//*[contains(@class, "mini-suggest__popup_visible")]//*[contains(@class, "mini-suggest__popup-spacer"' +
    ')])[last()]').then(elem => elem.click());

    await this.browser.$('.body_search_yes')
        .then(elem => elem.waitForDisplayed({reverse: true}));
}

async function clear() {
    await this.browser.$('.mini-suggest__input-clear').then(elem => elem.click());
    await this.browser.$('.mini-suggest_has-value_yes')
        .then(elem => elem.waitForDisplayed({reverse: true}));
}

async function input(str) {
    await this.browser.$('.mini-suggest__input').then(elem => elem.setValue(str));
    // Ожидание .mini-suggest_open, mini-suggest_has-value_yes недостаточно
    await this.browser.pause(500);
}

specs('Неосновные морды', function () {
    beforeEach(async function() {
        await this.browser.yaOpenMorda({yaru: true});
        await this.browser.$('.mini-suggest_js_inited').then(elem => elem.waitForDisplayed());
    });

    describe('ya.ru: стрелка', function () {
        it('Фокус на стрелке', async function() {
            await open.apply(this);
        });

        it('Блюр стрелки', async function () {
            await open.apply(this);
            await close.apply(this);
            await this.browser.assertView('blured', 'body');
        });

        it('Ввод текста', async function () {
            await open.apply(this);
            await input.apply(this, ['котики']);
            await this.browser.yaHideElement('.mini-suggest__popup-content');
            await this.browser.assertView('input', 'body');
        });

        it('Ввод текста и блюр', async function () {
            await open.apply(this);
            await input.apply(this, ['котики']);
            await close.apply(this);
            await this.browser.assertView('blured', 'body');
        });
    });

    describe('ya.ru: кнопки', function () {
        beforeEach(async function() {
            await open.apply(this);
            await input.apply(this, ['котики']);
        });

        it('Стирание текста в фокусе', async function() {
            await clear.apply(this);
            await this.browser.assertView('clear', 'body');
        });

        it('Текст стирается в блюре', async function() {
            await close.apply(this);
            await this.browser.assertView('unfocused', 'body');
            await clear.apply(this);
            await this.browser.assertView('clear-blured', 'body');
        });
    });
});
