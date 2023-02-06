const Page = require('./Page.js');

const counterNameField = '.form-field_type_input input';
const sitePathField = '.counter-edit__site2 span span input';
const licenseAgreementCheckbox = '.counter-edit__agreement-checkbox [type="checkbox"]';
const submitCreateCounter = '.counter-edit__submit';
const counterCodePreview = '.counter-edit-code__preview';

const counterNameLength = 10;

class CreateCounterPage extends Page {
    async open() {
        await this.browser.url('/add');
    }

    async createCounter() {
        await this.fillSiteName();
        await this.fillSitePath();
        await this.acceptAgreement();
        await this.createCountButton();

        const currentUrl =  await this.getUrl();
        return await Number(currentUrl.slice(currentUrl.lastIndexOf("/") + 1, currentUrl.indexOf("?")));
    }

    async fillSiteName() {
        await this.browser
            .element(counterNameField)
            .setValue(this.generateCounterName());
    }

    async fillSitePath() {
        await this.browser
            .element(sitePathField)
            .setValue(this.generateRandomSite());
    }

    async acceptAgreement() {
        await this.browser
            .click(licenseAgreementCheckbox);
    }

    async createCountButton() {
        await this.browser
            .waitForExist(submitCreateCounter)
            .scroll(submitCreateCounter)
            .click(submitCreateCounter)
            .waitForExist(counterCodePreview);
    }

    async isCodePreviewAllow() {
        return await this.browser
            .isExisting(counterCodePreview);
    }

    //Вспомогательные методы
    generateCounterName() {
        return `Счетчик ${this.getRandomString(counterNameLength)}`;
    }

    generateRandomSite() {
        return `${this.getRandomString(counterNameLength)}.ru`;
    }

}

module.exports = {
    CreateCounterPage,
};
