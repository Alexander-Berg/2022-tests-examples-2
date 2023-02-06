const steps = require('../../helpers/api/steps');
const pages = require('../../utils/passportPages');

/**
 * Тесты на тесты: запуск тестов в разных окружениях Паспорта
 */
hermione.only.in('chrome-desktop'); // Не зависит от браузера
describe('debug/env-tests', function() {
    let testEnv;

    beforeEach(async function() {
        testEnv = hermione.ctx.TEST_ENV;
    });
    afterEach(async function() {
        hermione.ctx.TEST_ENV = testEnv;
    });

    it.only('Создаём аккаунт и авторизуемся в dev-окружении', async function() {
        hermione.ctx.TEST_ENV = 'dev'; // TODO: use const

        const user = await steps.passport.registration.createEmptyUser();

        await this.browser.yaAuth(user);
        await this.browser.url(pages.PROFILE.getUrl());

        await this.browser.yaShouldBeAtUrl(pages.PROFILE);
    });

    it('Создаём аккаунт и авторизуемся в тестинге', async function() {
        hermione.ctx.TEST_ENV = 'test'; // TODO: use const

        const user = await steps.passport.registration.createEmptyUser();

        await this.browser.yaAuth(user);
        await this.browser.url(pages.PROFILE.getUrl());

        await this.browser.yaShouldBeAtUrl(`https://passport-test.yandex.${hermione.ctx.TEST_TLD}/profile`, true);
    });

    it('Создаём аккаунт и авторизуемся в rc', async function() {
        hermione.ctx.TEST_ENV = 'rc'; // TODO: use const

        const user = await steps.passport.registration.createEmptyUser();

        await this.browser.yaAuth(user);
        await this.browser.url(pages.PROFILE.getUrl());

        await this.browser.yaShouldBeAtUrl(`https://passport-rc.yandex.${hermione.ctx.TEST_TLD}/profile`, true);
    });

    it('Создаём аккаунт и авторизуемся в проде', async function() {
        hermione.ctx.TEST_ENV = 'prod'; // TODO: use const

        const user = await steps.passport.registration.createEmptyUser();

        await this.browser.yaAuth(user);
        await this.browser.url(pages.PROFILE.getUrl());

        await this.browser.yaShouldBeAtUrl(`https://passport.yandex.${hermione.ctx.TEST_TLD}/profile`, true);
    });
});
