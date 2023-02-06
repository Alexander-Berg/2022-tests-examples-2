const Page = require('./Page.js');

const addCounterButton = '.button2_theme_promo';
const demoCounterLink = '.header-wrapper__link';

class PromoPage extends Page {
    async open() {
        await this.browser.url('/promo');
    }

    async openDemoCounter() {
        await this.browser.waitForExist(demoCounterLink).click(demoCounterLink);
    }

    async clickStartUsing() {
        await this.browser
            .waitForExist(addCounterButton)
            .click(addCounterButton);
    }
}

module.exports = {
    PromoPage,
};
