'use strict';

specs('suggest', function () {
    it('Есть плейсхолдер', async function () {
        await this.browser.yaOpenMorda();
        await this.browser.$('.search2__placeholder').then(elem => elem.waitForDisplayed());
    });
    it('Навигационные подсказки', async function () {
        await this.browser.yaOpenMorda();
        await this.browser.$('.mini-suggest__input').then(elem => elem.setValue('вконтакте'));
        await this.browser.$('.mini-suggest__popup').then(elem => elem.waitForDisplayed());
        await this.browser.yaResourceRequested(/favicon\.yandex\.net.+vk\.com/, {timeout: 5000});
        await this.browser.$('.mini-suggest__item_type_nav').then(elem => elem.waitForDisplayed());
        await this.browser.assertView('popup', '.mini-suggest__item_type_nav', {
            tolerance: 10
        });
    
        await this.browser.keys('ArrowDown');
        await this.browser.yaResourceRequested(/favicon\.yandex\.net.+vk\.com/, {timeout: 5000});
        await this.browser.assertView('selected', '.mini-suggest__item_type_nav', {
            tolerance: 10
        });
        await this.browser.keys('Enter');
        await this.browser.switchWindow('https://vk.com');
    });
});