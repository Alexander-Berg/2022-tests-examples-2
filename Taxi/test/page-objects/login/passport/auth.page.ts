import {findElement, Undefinable} from '@txi-autotests/ts-utils';

import {AUTH_CONFIG} from '../../../config/auth';

import {BasePage} from './base.page';

class AuthPage extends BasePage {
    @findElement('div.AuthLoginInputToggle-type:nth-child(1) button')
    public mailToggle: Undefinable<ReturnType<typeof $>>;

    @findElement('div.AuthLoginInputToggle-type:nth-child(2) button')
    public phoneToggle: Undefinable<ReturnType<typeof $>>;

    public async login(username: string, password: string) {
        const inputUsername = await this.findInputUsername();
        /*
        * форма последовательная и каждое поле (логин->пароль)
        * показываются последовательно
        * поэтому кнопка одна и та же два раза
        * */
        const buttonSubmit = await this.findButtonSubmit();

        await inputUsername.setValue(username);
        await buttonSubmit.click();

        const inputPassword = await this.findInputPassword();

        await inputPassword.setValue(password);
        await buttonSubmit.click();
    }

    public async open() {
        return super.open(AUTH_CONFIG.PASSPORT.WELCOME_PATH);
    }

    protected async findInputUsername() {
        return $('#passp-field-login');
    }

    protected async findInputPassword() {
        return $('#passp-field-passwd');
    }

    protected async findButtonSubmit() {
        return $('button[type="submit"]');
    }

    public async findProfileLastName() {
        const element = await $('.personal-info__last');

        return element.getText();
    }

    public async findProfileFirstName() {
        const element = await $('.personal-info__first');

        return element.getText();
    }

    public async selectToAuthViaMail() {
        if (await this.phoneToggle?.getAttribute('data-t') === 'button:default') {
            await this.mailToggle?.click();
        }
    }
}

export const authPage = new AuthPage();
