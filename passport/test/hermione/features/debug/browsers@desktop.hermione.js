const pages = require('../../utils/passportPages');
const {commonUser} = require('../../utils/utils');

/**
 * Тесты на тесты: запуск тестов в разных браузерах
 */
describe('debug/browsers-tests', function() {
    it('Авторизуемся в домике в десктопных браузерах', async function() {
        const PO = this.PO;

        await this.browser.url(pages.AUTH.getUrl());

        await this.browser.yaSetValue(PO.auth.loginInput(), commonUser.login);
        await this.browser.click(PO.submitButton());

        await this.browser.yaSetValue(PO.auth.passwordInput(), commonUser.password);
        await this.browser.click(PO.submitButton());

        await this.browser.yaWaitForVisible('[data-page-type="profile.passportv2"]');
        await this.browser.yaShouldBeAtUrl(pages.PROFILE.getUrl());
    });
});
