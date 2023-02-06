const pages = require('../../utils/passportPages');

/**
 * Тесты на тесты: базовые сценарии для web
 */
describe('debug/web-tests', function() {
    it('Переходим на страницу с домиком при открытии /profile неавторизованным пользователем', async function() {
        await this.browser.url(pages.PROFILE.getUrl());

        await this.browser.yaShouldHaveVisibleText('.passp-title > span:nth-child(1)', 'Войдите с Яндекс ID');
    });

    it('Переходим на /profile авторизованным пользователем', async function() {
        await this.browser.yaAuth('yndx-killer'); // авторизация через TUS
        await this.browser.url(pages.PROFILE.getUrl());

        await this.browser.yaShouldHaveVisibleText('.personal-info-login__text', 'yndx-killer');
    });
});
