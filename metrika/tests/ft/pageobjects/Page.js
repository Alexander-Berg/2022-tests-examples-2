const header = '.header2';

const errorPopup = '.popup .error-message__message-content';
const bugOpener = '.mooa .mooa__opener';
const closeAppPopupBtn = '.metrika-app__close';

class Page {

    constructor(browser) {
        this.browser = browser;
    }

    Page(browser) {
        this.browser = browser;
    }

    async openMainUrl() {
        return this.browser.url('/');
    }

    async openUrl(url) {
        await this.browser.url(url);
    }

    async getUrl() {
        return this.browser.getUrl();
    }

    async refresh() {
        await this.browser.refresh();
    }

    async getTitle() {
        return this.browser.getTitle();
    }

    async closeAppPopup() {
        await this.browser.waitForExist(closeAppPopupBtn)
            .click(closeAppPopupBtn);
    }

    async getErrorMessage() {
        return await this.browser
            .waitForVisible(errorPopup)
            .getText(errorPopup);
    }

    async isBugVisible() {
        return this.browser
            .waitForVisible(header)
            .isVisible(bugOpener);
    }

    getRandomString(length) {
        let text = "";
        const possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

        for (var i = 0; i < length; i++)
            text += possible.charAt(Math.floor(Math.random() * possible.length));

        return text;
    }

    getRandomNumber(length) {
        return Number(Math.pow(10, length - 1) + Math.random() * (Math.pow(10, length) - Math.pow(10, length - 1))).toFixed();
    }
}

module.exports = Page;
