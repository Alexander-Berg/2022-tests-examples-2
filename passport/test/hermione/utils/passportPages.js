const {getPassportFrontendHost} = require('../testEnvironmentConfig');

class PassportPage {
    constructor(path) {
        this.path = path;
    }

    getUrl() {
        // синтаксический сахар для вызовов вида this.browser.url(page.AUTH.getUrl());
        return this.toString();
    }

    toString() {
        return `${getPassportFrontendHost() + this.path}`;
    }
}

const PassportPages = {
    AM: new PassportPage('/am'),
    AUTH: new PassportPage('/auth'),
    AUTH_ADD: new PassportPage('/auth/add'),
    AUTH_REG: new PassportPage('/auth/reg'),
    AUTH_REG_COMPLETE: new PassportPage('/auth/complete'),
    AUTH_RESTORE_PASSWORD: new PassportPage('/auth/restore/password'),
    AUTH_RESTORE_PASSWORD_CAPTCHA: new PassportPage('/auth/restore/password/captcha'),
    AUTH_RESTORE_PASSWORD_METHOD: new PassportPage('/auth/restore/password/method'),
    AUTH_RESTORE_PASSWORD_METHOD_CONFIRM: new PassportPage('/auth/restore/password/method-confirm'),
    AUTH_RESTORE_PASSWORD_FINISH: new PassportPage('/auth/restore/password/finish'),
    AUTH_RESTORE_PASSWORD_BIND_PHONE: new PassportPage('/auth/restore/password/bind-phone'),
    AUTH_USER_VALIDATE: new PassportPage('/auth/user-validate'),
    AUTH_WELCOME: new PassportPage('/auth/welcome'),
    FAMILY_MAIN: new PassportPage('/profile/family'),
    FAMILY_INVITE: new PassportPage('/profile/family/invite'),
    FAMILY_INVITE_CONFIRM: new PassportPage('/profile/family/invite/$inviteId'),
    FAMILY_PAY_LIMITS: new PassportPage('/profile/family/limits'),
    REGISTRATION: new PassportPage('/registration'),
    PROFILE: new PassportPage('/profile'),
    PROFILE_SOCIAL: new PassportPage('/profile/social'),
    PROFILE_UPGRADE: new PassportPage('/profile/upgrade')
};

module.exports = PassportPages;
