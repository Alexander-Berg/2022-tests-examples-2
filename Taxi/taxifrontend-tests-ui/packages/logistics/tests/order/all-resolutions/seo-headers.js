const orderPage = require('../../../pageobjects/order/order-page');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница заказа /order', () => {
    it('SEO заголовки', async function () {
        allureReporter.addTestId('taxiweb-2084');

        await browser.url('/order/moscow/cargo');

        await expect(browser.$('h1')).toHaveText('Доставка грузов по Москве и области')

        await browser.$(orderPage.courierTariffBtn).click();

        await expect(browser.$('h1')).toHaveText('Доставка курьером по Москве и области')
    });
});
