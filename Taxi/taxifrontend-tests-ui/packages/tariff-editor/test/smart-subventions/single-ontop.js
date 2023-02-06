const auth = require('../../support/auth');
const sub = require('../../pageobjects/smart-subventions/smart-subventions.js');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Создание single-ontop', () => {
    it('Создание субсидии', async () => {
        allureReporter.addTestId('taxiweb-1410');
        await auth();
        await sub.openSub();
        await browser.$(sub.create).click();
        await browser.$(sub.subventionType).click();
        await browser.$(sub.subventionTypeOnTop).click();
        await sub.fillSubventionsForm();
    });
});
