const auth = require('../../support/auth');
const sub = require('../../pageobjects/smart-subventions/smart-subventions.js');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Создание single-ride', () => {
    it('Создание субсидии', async () => {
        allureReporter.addTestId('taxiweb-1133');
        await auth();
        await sub.openSub();
        await browser.$(sub.create).click();
        await sub.fillSubventionsForm();
    });
});
