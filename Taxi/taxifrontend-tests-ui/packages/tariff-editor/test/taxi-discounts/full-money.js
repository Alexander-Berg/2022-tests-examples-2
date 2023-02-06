const auth = require('../../support/auth');
const discountFull = require('../../pageobjects/taxi-discounts/taxi-discounts.js');
const {waitExistSelectorAndReload} = require('../../support/helpers');
const allureReporter = require('@wdio/allure-reporter').default;
const nameOfDiscount = Date.now() + 'full-money';

describe('Создание полной скидки (Деньгами)', () => {
    it('Создание скидки такси', async () => {
        allureReporter.addTestId('taxiweb-2058');
        await auth();
        await discountFull.openTaxiDiscount(`full_money_discounts`);
        await browser.$(discountFull.discountName).setValue(nameOfDiscount);
        await browser.$(discountFull.classOfDiscounts).setValue('dasha_test1');
        await browser.keys('Enter');
        await browser.$(discountFull.zone).click();
        await browser.$(discountFull.zone).setValue('minsk');
        await browser.$(discountFull.zoneCurrent).click();
        await browser.$(discountFull.prioritized).click();
        await browser.$(discountFull.discountPercentMoney).setValue('1');
        await browser.$(discountFull.ticket).setValue('TAXIRATE-91');
        await browser.$(discountFull.submit).click();
        await browser.$(discountFull.acceptButton).click();
        await browser.$(discountFull.notification).isExisting();
        //ждем пока выполнится драфт(статус 'Выполнен успешно')
        await waitExistSelectorAndReload(21000, discountFull.successLabel);
    });
});
