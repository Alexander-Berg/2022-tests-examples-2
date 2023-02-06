const pages = require('../../utils/passportPages');
const {commonUser} = require('../../utils/utils');

/**
 * Тесты на тесты: запуск тестов на разных доменах Паспорта
 */
describe('debug/domains-tests', function() {
    it('Авторизуемся в домике на RU домене', async function() {});
    it('Авторизуемся в домике на COM.TR домене', async function() {
        const PO = this.PO;

        await this.browser.url(pages.AUTH.getUrl());

        await this.browser.yaSetValue(PO.auth.loginInput(), commonUser.login);
        await this.browser.click(PO.submitButton());

        await this.browser.yaSetValue(PO.auth.passwordInput(), commonUser.password);
        await this.browser.click(PO.submitButton());

        await this.browser.yaShouldBeAtUrl(pages.PROFILE);
    });
});
