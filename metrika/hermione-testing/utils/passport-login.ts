declare let hermione: any;

export async function passportLogin() {
    const timeoutMS = 10000;
    const loginInputSelector = '#passp-field-login';
    const passwodInputSelector = '#passp-field-passwd';
    const signInButtonSelector = '.passp-sign-in-button';
    const profileSelector = '.profile';

    const { username, password } = hermione.ctx.user;

    await this.browser.url('https://passport.yandex.ru/');

    // ввести логин и нажать кнопку
    await this.browser.$(loginInputSelector).setValue(username);
    await this.browser.$(signInButtonSelector).click();

    // дождаться загрузки поля для ввода пароля
    await this.browser.waitForExist(passwodInputSelector);

    // ввести пароль и нажать кнопку
    await this.browser.$(passwodInputSelector).setValue(password);
    await this.browser.$(signInButtonSelector).click();

    // дождаться завершения авторизации и перехода на страницу с профилем
    await this.browser.waitForExist(profileSelector, timeoutMS);
}
