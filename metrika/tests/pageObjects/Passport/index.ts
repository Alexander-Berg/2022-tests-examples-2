import { Page } from '../Page';
import { helpSelectors } from 'shared/testIds';

type User = {
    username: string;
    password: string;
};

class Passport extends Page {
    get loginInput() {
        return this.browser.$(helpSelectors.passport.loginInput);
    }

    get passwordInput() {
        return this.browser.$(helpSelectors.passport.passwordInput);
    }

    get submitButton() {
        return this.browser.$(helpSelectors.passport.submitButton);
    }

    get skipButton() {
        return this.browser.$(helpSelectors.passport.skipButton);
    }

    async submit() {
        await this.submitButton.click();

        try {
            await this.skipButton.waitForVisible(1000);
        } catch (error) {
            return;
        }

        await this.skipButton.click();
        await this.browser.customWaitForRedirect();
    }

    async login(user: User) {
        await this.browser.url('https://passport.yandex.ru/');

        await this.loginInput.customWaitForExist();
        await this.loginInput.setValue(user.username);

        await this.submitButton.click();
        await this.passwordInput.customWaitForExist();
        await this.passwordInput.setValue(user.password);

        await this.submit();
    }
}

export { Passport };
