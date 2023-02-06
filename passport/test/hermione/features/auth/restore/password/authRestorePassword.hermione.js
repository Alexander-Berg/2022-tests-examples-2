const pages = require('../../../../utils/passportPages');
const steps = require('../../../../helpers/api/steps');
const {commonUser, commonWithControlQuestion} = require('../../../../utils/utils');

/* TODO:
    - удалять создаваемые аккаунты после тестов
    - проверять привязку номера в конце восстановления
    - шаги с проверкой номера телефона и email'a 😱
 */

describe('/auth/restore/password', function() {
    beforeEach(async function() {
        await this.browser.url(pages.AUTH_RESTORE_PASSWORD.getUrl());
    });

    it('Получаем предложение ввести логин при открытии по прямой ссылке', async function() {
        const PO = this.PO;

        await this.browser.yaShouldHaveVisibleText(
            PO.auth.title(),
            'Введите ID, для которого вы хотите восстановить доступ'
        );
    });

    it('Попадаем на экран капчи после ввода логина', async function() {
        const PO = this.PO;

        await this.browser.yaSetValue(PO.auth.loginInput(), commonUser.login);
        await this.browser.click(PO.submitButton());

        await this.browser.yaWaitForVisible(PO.auth.captchaImage());
        await this.browser.yaWaitForVisible(PO.auth.captchaInput());
        await this.browser.yaShouldBeAtUrl(pages.AUTH_RESTORE_PASSWORD_CAPTCHA);
    });

    it('Попадаем на экран ввода КО после прохождения капчи', async function() {
        const PO = this.PO;

        await this.browser.yaSetValue(PO.auth.loginInput(), commonUser.login);
        await this.browser.click(PO.submitButton());
        await this.browser.yaPassCaptcha(PO);

        await this.browser.yaShouldBeAtUrl(pages.AUTH_RESTORE_PASSWORD_METHOD);
    });

    it('Получаем ошибку при неправильном ответе на капчу', async function() {
        const PO = this.PO;

        await this.browser.yaSetValue(PO.auth.loginInput(), commonUser.login);
        await this.browser.click(PO.submitButton());

        await this.browser.yaSetValue(PO.auth.captchaInput(), 'incorrect captcha');
        await this.browser.click(PO.submitButton());

        await this.browser.yaShouldHaveVisibleText(
            PO.auth.errorField(),
            'Вы неверно ввели символы. Попробуйте еще раз'
        );
    });

    it('Получаем ошибку при неправильном ответе на контрольный вопрос', async function() {
        const PO = this.PO;

        await this.browser.yaSetValue(PO.auth.loginInput(), commonWithControlQuestion.login);
        await this.browser.click(PO.submitButton());
        await this.browser.yaPassCaptcha(PO);

        // question check
        await this.browser.yaSetValue(PO.auth.controlAnswerInput(), 'incorrect answer');
        await this.browser.click(PO.submitButton());

        await this.browser.yaShouldHaveVisibleText(
            PO.auth.errorField(),
            'Ответ неверный. Возможно, вы сделали опечатку или выбрали не ту раскладку клавиатуры.'
        );
    });

    it('Попадаем на экран ввода нового пароля после проверки кв-ко', async function() {
        const PO = this.PO;

        await this.browser.yaSetValue(PO.auth.loginInput(), commonWithControlQuestion.login);
        await this.browser.click(PO.submitButton());
        await this.browser.yaPassCaptcha(PO);

        // question check
        await this.browser.yaSetValue(PO.auth.controlAnswerInput(), commonWithControlQuestion.controlAnswer);
        await this.browser.click(PO.submitButton());

        await this.browser.yaShouldBeAtUrl(pages.AUTH_RESTORE_PASSWORD_FINISH);
    });

    it('Попадаем на экран привязки телефона после ввода нового пароля', async function() {
        const PO = this.PO;
        const user = await steps.passport.registration.createUserWithControlQuestion();

        await this.browser.yaSetValue(PO.auth.loginInput(), user.login);
        await this.browser.click(PO.submitButton());
        await this.browser.yaPassCaptcha(PO);

        // question check
        await this.browser.yaSetValue(PO.auth.controlAnswerInput(), user.controlAnswer);
        await this.browser.click(PO.submitButton());

        // password screen
        await this.browser.yaSetValue(PO.auth.passwordInput(), 'new_pwd_simple123456');
        await this.browser.yaSetValue(PO.auth.passwordConfirmInput(), 'new_pwd_simple123456');
        await this.browser.yaWaitForVisible(PO.auth.passwordEyeToggle());
        await this.browser.click(PO.submitButton());

        await this.browser.yaShouldBeAtUrl(pages.AUTH_RESTORE_PASSWORD_BIND_PHONE);
    });
});
