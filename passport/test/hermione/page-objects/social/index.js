const El = require('@yandex-int/bem-page-object').Entity;

const mailOAuth = {};

mailOAuth.form = new El('.auth-dialog,.login-form');
mailOAuth.loginInput = new El('#login');
mailOAuth.passwordInput = new El('#password');
mailOAuth.submit = new El('[type="submit"]');

module.exports = {
    mailOAuth
};
