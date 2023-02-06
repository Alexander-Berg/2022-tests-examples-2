const auth = require('../../support/auth');
const discountBin = require('../../pageobjects/taxi-discounts/taxi-discounts.js');
const {waitExistSelectorAndReload} = require('../../support/helpers');
const allureReporter = require('@wdio/allure-reporter').default;
const nameOfDiscount = Date.now() + 'bin-cashback';

describe('Создание скидки по BINам (Кешбэком)', () => {
    it('Создание скидки такси', async () => {
        allureReporter.addTestId('taxiweb-2053');
        await auth();
        await discountBin.openTaxiDiscount(`payment_method_cashback_discounts`);
        await browser.$(discountBin.discountName).setValue(nameOfDiscount);
        await browser.$(discountBin.zone).click();
        await browser.$(discountBin.zone).setValue('minsk');
        await browser.$(discountBin.zoneCurrent).click();
        await browser.$(discountBin.prioritySpecific).scrollIntoView();
        await browser.$(discountBin.prioritySpecific).click();
        await browser.$(discountBin.priorityForAll).click();
        await browser.$(discountBin.prioritized).click();
        await browser.$(discountBin.discountPercentCashback).setValue('1');
        await browser.$(discountBin.ticket).setValue('TAXIRATE-91');
        await browser.$(discountBin.submit).click();
        await browser.$(discountBin.acceptButton).click();
        await browser.$(discountBin.notification).isExisting();
        //ждем пока выполнится драфт(статус 'Выполнен успешно')
        await waitExistSelectorAndReload(21000, discountBin.successLabel);
    });
});
