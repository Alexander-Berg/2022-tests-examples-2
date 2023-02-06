const Page = require('./Page.js');

const loginField = '[name="login"]';
const passwordField = '[name="passwd"]';
const submitButton = '[type="submit"]';

class Passport extends Page {
    async login(user) {
        let oldUrl;
        return this.browser
            .url('https://passport.yandex.ru/')
            .waitForExist(loginField)
            .setValue(loginField, user.username)
            .click(submitButton)
            .waitForExist(passwordField)
            .setValue(passwordField, user.password)
            .getUrl()
            .then((url) => {
                oldUrl = url;
            })
            .click(submitButton)
            .waitUntil(function PassportWaitUntil() {
                return this.getUrl().then((url) => url !== oldUrl);
            }, 5000);
    }
}

module.exports = {
    Passport,
};
