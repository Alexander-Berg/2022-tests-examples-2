const orderPage = require('../../../pageobjects/order/order-page');
const allureReporter = require('@wdio/allure-reporter').default;
const {fillAddress} = require('../../../support/helpers');

describe('Страница заказа /order', () => {
    it('Очистка адресов', async function () {
        allureReporter.addTestId('taxiweb-1595');

        const addressFrom = 'Садовническая улица, 82с2';
        const addressTo = 'улица Льва Толстого, 16';
        const addressToSecond = 'Зубовский бульвар, 2с1';
        await orderPage.mockSuggestToMoscow();
        await orderPage.open('/order/express');
        await browser.mockRestoreAll();
        await fillAddress(orderPage.addressFrom, addressFrom);
        await fillAddress(orderPage.addressTo, addressTo);
        await browser.$(orderPage.addAddressBtn).scrollIntoView();
        await browser.$(orderPage.addAddressBtn).click();
        await fillAddress(orderPage.addressToSecond, addressToSecond);

        await browser.$(orderPage.clearAddressBtnFirst).click();
        await browser.$(orderPage.clearAddressBtnSecond).scrollIntoView();
        await browser.$(orderPage.clearAddressBtnSecond).click();

        await expect(browser.$(orderPage.addressFrom)).toHaveValue('');
        await expect(browser.$(orderPage.addressTo)).toHaveValue(addressToSecond);
    });
});
