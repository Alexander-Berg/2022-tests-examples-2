const auth = require('../../support/auth');
const discountExp = require('../../pageobjects/taxi-discounts/taxi-discounts.js');
const {waitExistSelectorAndReload} = require('../../support/helpers');
const allureReporter = require('@wdio/allure-reporter').default;
const nameOfDiscount = Date.now() + 'exp-cashback';

describe('Создание экспериментальной скидки (Кешбэком)', () => {
    it('Создание скидки такси', async () => {
        allureReporter.addTestId('taxiweb-2061');
        await auth();
        await discountExp.openTaxiDiscount(`experimental_cashback_discounts`);
        await browser.$(discountExp.discountName).setValue(nameOfDiscount);
        await browser.keys('Enter');
        await browser.$(discountExp.zone).click();
        await browser.$(discountExp.zone).setValue('minsk');
        await browser.$(discountExp.zoneCurrent).click();
        await browser.$(discountExp.prioritized).click();
        await browser.$(discountExp.discountPercentCashback).setValue('1');
        await browser.$(discountExp.ticket).setValue('TAXIRATE-91');
        await browser.$(discountExp.submit).click();
        await browser.$(discountExp.acceptButton).click();
        await browser.$(discountExp.notification).isExisting();
        //ждем пока выполнится драфт(статус 'Выполнен успешно')
        await waitExistSelectorAndReload(21000, discountExp.successLabel);
    });
});
