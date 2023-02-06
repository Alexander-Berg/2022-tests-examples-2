const orderPage = require('../../../pageobjects/order/order-page');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница заказа /order', () => {
    it('Привязка карты, открытие модалки', async function () {
        allureReporter.addTestId('taxiweb-1596');

        await orderPage.authorizeAndOpen('/order');

        await browser.$(orderPage.paymethodCash).scrollIntoView();
        await browser.$(orderPage.paymethodCash).click();
        await browser.$(orderPage.modalAddCardBtn).click();

        await expect(browser.$('//*[text()="Добавить карту"]')).toBeDisplayed();
    });
});
