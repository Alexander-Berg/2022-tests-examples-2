const orderPage = require('../../../pageobjects/order/order-page');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница заказа /order', () => {
    it('Переключение тарифов', async function () {
        allureReporter.addTestId('taxiweb-1592');

        await orderPage.open('/order');

        await browser.$(orderPage.expressTariffBtn).click();
        await expect(browser.$(orderPage.recipientPhone)).toBeDisplayed();

        await browser.$(orderPage.cargoTariffBtn).click();
        await expect(browser.$(orderPage.recipientPhone)).not.toBeDisplayed();

        await browser.$(orderPage.courierTariffBtn).click();
        await expect(browser.$(orderPage.recipientPhone)).toBeDisplayed();
    });
});
